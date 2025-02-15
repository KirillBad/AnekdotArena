from aiogram import Router, F
from aiogram.types import CallbackQuery, LabeledPrice, Message, PreCheckoutQuery
from aiogram.fsm.context import FSMContext
from anecdotes.states import RateStates
from payments.kbs import send_gift_kb, write_gift_text_kb, SendGiftCallbackFactory
from sqlalchemy.ext.asyncio import AsyncSession
from anecdotes.kbs import rate_anecdote_kb, pagination_anecdotes_kb, back_to_start_kb
from aiogram.methods import SendGift
from users.dao import UserDAO
from users.schemas import UserIDModel, TelegramIDModel
from config_reader import bot
from payments.schemas import GiftTextModel, GiftModel, DonationAmountModel, DonationModel
from pydantic import ValidationError
from payments.dao import GiftDAO, DonationDAO
from aiogram.filters.command import Command
from users.kbs import contact_us_kb
from users.utils import get_start_text
from users.states import UserStates

payments_router = Router()


@payments_router.callback_query(F.data == "select_gift")
async def start_send_gift(callback: CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    await state.update_data(previous_state=current_state)
    await state.set_state(RateStates.selecting_gift)
    await callback.message.edit_reply_markup(
        reply_markup=send_gift_kb(),
    )


@payments_router.callback_query(
    SendGiftCallbackFactory.filter(F.action == "gift"), RateStates.selecting_gift
)
async def process_send_gift(
    callback: CallbackQuery, callback_data: SendGiftCallbackFactory, state: FSMContext
):
    await callback.answer()

    await state.set_state(RateStates.writing_gift_text)

    await state.update_data(
        gift_id=callback_data.gift_id,
        gift_emoji=callback_data.gift_emoji,
        amount=callback_data.value,
    )

    await callback.message.edit_text(
        text=f"💌 Напишите подпись к подарку {callback_data.gift_emoji}",
        reply_markup=write_gift_text_kb(),
    )


@payments_router.message(F.text, RateStates.writing_gift_text)
@payments_router.callback_query(F.data == "skip_text", RateStates.writing_gift_text)
async def process_send_gift(
    event: Message | CallbackQuery,
    state: FSMContext,
):
    gift_text = ""
    if isinstance(event, Message):
        try:
            validated_text = GiftTextModel(text=event.text)
            gift_text = validated_text.text
            message = event
        except ValidationError as e:
            error_message = "❌ Ошибка\n\n"
            if "string_too_long" in str(e):
                error_message += "Текст подписи не должен превышать 255 символов"
            else:
                error_message += f"{str(e)}"
            await event.answer(
                error_message + "\n\n🔁 Отправьте исправленный текст",
                reply_markup=write_gift_text_kb(),
            )
    else:
        await event.answer()
        message = event.message

    await state.update_data(gift_text=gift_text)

    data = await state.get_data()
    gift_emoji = data.get("gift_emoji")
    amount = data.get("amount")

    await message.reply_invoice(
        title=f"Отправить подарок {gift_emoji} автору",
        description="Автор анекдота получит подарок выбранный вами подарок",
        payload="send_gift",
        provider_token="",
        prices=[LabeledPrice(label="XTR", amount=amount)],
        currency="XTR",
    )


@payments_router.callback_query(F.data == "back", RateStates.selecting_gift)
async def handle_back(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    previous_state = data.get("previous_state")
    if previous_state == RateStates.watching_top_anecdotes:
        await state.set_state(RateStates.watching_top_anecdotes)
        await callback.message.edit_reply_markup(
            reply_markup=pagination_anecdotes_kb(data.get("page"), 10, "top_anecdotes"),
        )
    else:
        await state.set_state(RateStates.waiting_for_rate)
        await callback.message.edit_reply_markup(
            reply_markup=rate_anecdote_kb(),
        )


@payments_router.callback_query(F.data == "back", RateStates.writing_gift_text)
async def handle_back(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    await state.set_state(RateStates.selecting_gift)

    previous_state = data.get("previous_state")
    if previous_state == RateStates.watching_top_anecdotes:
        top_rates = data.get("top_rates")
        page = data.get("page")
        rating = f"{top_rates[page - 1]['avg_rating']:.2f}".rstrip("0").rstrip(".")

        await callback.message.edit_text(
            text=f"{top_rates[page - 1]['content']}\n\n📈 Рейтинг: {rating}",
            reply_markup=send_gift_kb(),
        )
    else:
        await callback.message.edit_text(
            text=data.get("anecdote_content"),
            reply_markup=send_gift_kb(),
        )


@payments_router.pre_checkout_query(RateStates.writing_gift_text)
async def pre_checkout_gift_handler(
    pre_checkout_query: PreCheckoutQuery, state: FSMContext
):
    await pre_checkout_query.answer(ok=True)


@payments_router.pre_checkout_query(UserStates.donating_to_prize_fund)
async def pre_checkout_donation_handler(
    pre_checkout_query: PreCheckoutQuery, state: FSMContext
):
    await pre_checkout_query.answer(ok=True)


@payments_router.message(F.successful_payment, RateStates.writing_gift_text)
async def on_successful_payment(
    message: Message,
    state: FSMContext,
    session_without_commit: AsyncSession,
    session_with_commit: AsyncSession,
):
    data = await state.get_data()
    user = await UserDAO.find_one_or_none(
        session=session_without_commit,
        filters=UserIDModel(id=data.get("anecdote_author_id")),
    )

    await bot(
        SendGift(
            user_id=user.telegram_id,
            gift_id=data.get("gift_id"),
            text=data.get("gift_text"),
        )
    )

    values = GiftModel(
        from_user_id=data.get("user_id"),
        to_user_id=data.get("anecdote_author_id"),
        gift_id=data.get("gift_id"),
        text=data.get("gift_text"),
        telegram_payment_charge_id=message.successful_payment.telegram_payment_charge_id,
    )

    await GiftDAO.add(session=session_with_commit, values=values)

    previous_state = data.get("previous_state")
    await state.set_state(RateStates.selecting_gift)
    if previous_state == RateStates.watching_top_anecdotes:
        await state.set_state(RateStates.watching_top_anecdotes)

        top_rates = data.get("top_rates")
        page = data.get("page")
        rating = f"{top_rates[page - 1]['avg_rating']:.2f}".rstrip("0").rstrip(".")

        await message.answer(
            text=f"{top_rates[page - 1]['content']}\n\n📈 Рейтинг: {rating}",
            reply_markup=send_gift_kb(),
        )
    else:
        await message.answer(
            text=data.get("anecdote_content"), reply_markup=rate_anecdote_kb()
        )


@payments_router.message(Command("paysupport"))
async def pay_support_handler(message: Message):
    await message.answer(
        text="⚠️ Отправленные подарки и пожертвования в призовой фонд не подразумевают возврат средств.\n\n💸 Если вы хотите вернуть средства, свяжитесь с нами.",
        reply_markup=contact_us_kb(),
    )


@payments_router.callback_query(F.data == "donate_to_prize_fund")
async def donate_to_prize_fund(callback: CallbackQuery, state: FSMContext):
    await state.set_state(UserStates.donating_to_prize_fund)
    await callback.message.edit_text(
        text="💸 Отправьте сумму пожертвования в призовой фонд",
        reply_markup=back_to_start_kb(),
    )


@payments_router.message(F.text, UserStates.donating_to_prize_fund)
async def process_donate_to_prize_fund(message: Message, state: FSMContext):
    await state.update_data(amount=message.text)

    try:
        validated_amount = DonationAmountModel(amount=message.text)
    except Exception:
        await message.answer(
            "❌ Пожалуйста, введите целое число\n\n" "✏️ Например: 100",
            reply_markup=back_to_start_kb(),
        )

    await message.reply_invoice(
        title=f"Пополнение призового фонда",
        description=f"Пожертвование в призовой фонд на сумму {validated_amount.amount} ⭐️",
        payload="donate_to_prize_fund",
        provider_token="",
        prices=[LabeledPrice(label="XTR", amount=validated_amount.amount)],
        currency="XTR",
    )


@payments_router.message(F.successful_payment, UserStates.donating_to_prize_fund)
async def on_successful_payment(
    message: Message,
    state: FSMContext,
    session_without_commit: AsyncSession,
    session_with_commit: AsyncSession,
):
    data = await state.get_data()

    user = await UserDAO.find_one_or_none(
        session=session_without_commit,
        filters=TelegramIDModel(telegram_id=message.from_user.id),
    )

    values = DonationModel(
        user_id=user.id,
        amount=data.get("amount"),
        telegram_payment_charge_id=message.successful_payment.telegram_payment_charge_id,
    )

    await DonationDAO.add(session=session_with_commit, values=values)

    await state.clear()
    text, kb = await get_start_text(message, session_without_commit)
    await message.answer("✅ Спасибо за пожертвование!")
    await message.answer(text, reply_markup=kb)
