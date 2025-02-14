from aiogram import Router, F
from aiogram.types import CallbackQuery, LabeledPrice, Message, PreCheckoutQuery
from aiogram.fsm.context import FSMContext
from anecdotes.states import RateStates
from payments.kbs import send_gift_kb
from sqlalchemy.ext.asyncio import AsyncSession
from anecdotes.kbs import rate_anecdote_kb, pagination_anecdotes_kb
from payments.kbs import SendGiftCallbackFactory
from aiogram.methods import SendGift
from users.dao import UserDAO
from users.schemas import UserIDModel
from config_reader import bot

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
    await state.update_data(gift_id=callback_data.gift_id)
    await callback.message.reply_invoice(
        title=f"Отправить подарок {callback_data.gift_emoji} автору",
        description="Автор анекдота получит подарок выбранный вами подарок",
        payload="test",
        provider_token="",
        prices=[LabeledPrice(label="XTR", amount=callback_data.value)],
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

@payments_router.pre_checkout_query(RateStates.selecting_gift)
async def pre_checkout_handler(pre_checkout_query: PreCheckoutQuery, state: FSMContext):  
    await pre_checkout_query.answer(ok=True)

@payments_router.message(F.successful_payment, RateStates.selecting_gift)
async def on_successful_payment(
    message: Message, state: FSMContext,  session_without_commit: AsyncSession
):
    data = await state.get_data()
    user = await UserDAO.find_one_or_none(session=session_without_commit, filters=UserIDModel(id=data.get("anecdote_author_id")))
    await bot(SendGift(
        user_id=user.telegram_id,
        gift_id=data.get("gift_id"),
    ))
    await state.set_state(RateStates.waiting_for_rate)
    await message.answer(text=data.get("anecdote_content"), reply_markup=rate_anecdote_kb())
