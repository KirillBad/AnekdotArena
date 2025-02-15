from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from anecdotes.utils import send_next_anecdote
from sqlalchemy.ext.asyncio import AsyncSession
from anecdotes.dao import AnecdoteDAO, RateDAO
from users.dao import UserDAO
from users.utils import get_start_text
from users.schemas import TelegramIDModel
from anecdotes.states import AnecdoteStates, RateStates
from anecdotes.kbs import (
    RateCallbackFactory,
    rated_anecdote_kb,
    back_to_start_kb,
    pagination_anecdotes_kb,
    PaginationCallbackFactory,
    reported_anecdote_kb,
)
from anecdotes.schemas import RateModel, RateModelUserId, AnecdoteFilter, AnecdoteUpdate, AnecdoteModel
from payments.dao import DonationDAO

anecdote_router = Router()


@anecdote_router.callback_query(F.data == "write_anecdote")
async def start_write_anecdote(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        text="✍️ Напишите анекдот\n\n✏️ Отправьте его в чат",
        reply_markup=back_to_start_kb(),
    )
    await state.set_state(AnecdoteStates.waiting_for_text)


@anecdote_router.message(F.text, AnecdoteStates.waiting_for_text)
async def process_anecdote(
    message: Message,
    state: FSMContext,
    session_with_commit: AsyncSession,
    session_without_commit: AsyncSession,
):
    text = message.text
    error_message = "❌ Ошибка\n\n"

    user = await UserDAO.find_one_or_none(
        session=session_with_commit,
        filters=TelegramIDModel(telegram_id=message.from_user.id),
    )

    try:
        values = AnecdoteModel(content=text, user_id=user.id)
        await AnecdoteDAO.add(session=session_with_commit, values=values)
        await state.clear()
        text, kb = await get_start_text(message, session_without_commit)
        await message.answer("✅ Ваш анекдот успешно сохранен!")
        await message.answer(text, reply_markup=kb)
    except ValidationError as e:
        error_str = str(e)
        if "Ссылки в анекдотах запрещены" in error_str:
            error_message += "Ссылки в анекдотах запрещены"
        elif "string_too_short" in error_str:
            error_message += "Текст анекдота должен содержать минимум 5 символов!"
        elif "string_too_long" in error_str:
            error_message += "Текст анекдота не должен превышать 3900 символов!"
        else:
            error_message += f"{error_str}"
        await message.answer(
            error_message + "\n\n🔁 Отправьте исправленный текст",
            reply_markup=back_to_start_kb(),
        )


@anecdote_router.callback_query(F.data == "rate_anecdote")
async def rate_anecdote(
    callback: CallbackQuery, state: FSMContext, session_without_commit: AsyncSession
):
    await callback.answer()

    user = await UserDAO.find_one_or_none(
        session=session_without_commit,
        filters=TelegramIDModel(telegram_id=callback.from_user.id),
    )

    rated_anecdotes = await RateDAO.find_all(
        session_without_commit, filters=RateModelUserId(user_id=user.id)
    )

    rated_anecdote_ids = [rate.anecdote_id for rate in rated_anecdotes]

    await send_next_anecdote(
        session_without_commit, state, rated_anecdote_ids, user.id, callback.message
    )


@anecdote_router.callback_query(
    RateCallbackFactory.filter(F.action == "rate"), RateStates.waiting_for_rate
)
async def process_rate(
    callback: CallbackQuery,
    callback_data: RateCallbackFactory,
    state: FSMContext,
    session_with_commit: AsyncSession,
    session_without_commit: AsyncSession,
):

    data = await state.get_data()
    anecdote_id = data.get("anecdote_id")
    user_id = data.get("user_id")
    rated_anecdote_ids = data.get("rated_anecdote_ids", [])

    rated_anecdote_ids.append(anecdote_id)
    await RateDAO.add(
        session_with_commit,
        values=RateModel(
            anecdote_id=anecdote_id, user_id=user_id, rating=callback_data.value
        ),
    )

    await callback.message.edit_reply_markup(
        reply_markup=rated_anecdote_kb(callback_data.value),
    )

    await send_next_anecdote(
        session_without_commit, state, rated_anecdote_ids, user_id, callback.message
    )


@anecdote_router.callback_query(F.data == "top_anecdotes")
async def top_anecdotes(
    callback: CallbackQuery, state: FSMContext, session_without_commit: AsyncSession
):
    await state.set_state(RateStates.watching_top_anecdotes)

    user = await UserDAO.find_one_or_none(
        session=session_without_commit,
        filters=TelegramIDModel(telegram_id=callback.from_user.id),
    )

    prize_pool = await DonationDAO.sum_amount(session_without_commit)

    prize_distribution = {0: 0.5, 1: 0.3, 2: 0.2}

    top_rates = await RateDAO.get_top_anecdotes(session_without_commit)

    serializable_top = [
        {
            "id": record.anecdote_id,
            "content": record.content,
            "user_id": record.user_id,
            "avg_rating": float(record.avg_rating) if record.avg_rating else 0,
            "prize": int(prize_pool * prize_distribution.get(i, 0)) if i < 3 else 0,
        }
        for i, record in enumerate(top_rates)
    ]

    await state.update_data(
        top_rates=serializable_top,
        anecdote_author_id=serializable_top[0]["user_id"],
        page=1,
        user_id=user.id,
    )

    rating = f"{serializable_top[0]['avg_rating']:.2f}".rstrip("0").rstrip(".")
    prize_text = (
        f"\n💸 Возможный выигрыш: {serializable_top[0]['prize']} ⭐️"
        if serializable_top[0]["prize"] > 0
        else ""
    )
    await callback.message.edit_text(
        text=f"{serializable_top[0]['content']}\n\n📈 <b>Рейтинг: {rating}{prize_text}</b>",
        reply_markup=pagination_anecdotes_kb(1, 10, "top_anecdotes"),
    )


@anecdote_router.callback_query(
    PaginationCallbackFactory.filter(F.action == "select_page"),
    RateStates.watching_top_anecdotes,
)
async def process_next_top_anecdotes(
    callback: CallbackQuery, callback_data: PaginationCallbackFactory, state: FSMContext
):
    data = await state.get_data()
    top_rates = data.get("top_rates")
    rating = f"{top_rates[callback_data.page - 1]['avg_rating']:.2f}".rstrip(
        "0"
    ).rstrip(".")
    prize_text = (
        f"\n💸 Возможный выигрыш: {top_rates[callback_data.page - 1]['prize']} ⭐️"
        if top_rates[callback_data.page - 1]["prize"] > 0
        else ""
    )
    await state.update_data(
        anecdote_author_id=top_rates[callback_data.page - 1]["user_id"],
        page=callback_data.page,
    )
    await callback.message.edit_text(
        text=f"{top_rates[callback_data.page - 1]['content']}\n\n📈 <b>Рейтинг: {rating}{prize_text}</b>",
        reply_markup=pagination_anecdotes_kb(callback_data.page, 10, "top_anecdotes"),
    )


@anecdote_router.callback_query(
    F.data == "report_anecdote", RateStates.waiting_for_rate
)
async def report_anecdote(
    callback: CallbackQuery,
    state: FSMContext,
    session_with_commit: AsyncSession,
    session_without_commit: AsyncSession,
):
    data = await state.get_data()
    anecdote_id = data.get("anecdote_id")
    user_id = data.get("user_id")
    anecdote_report_count = data.get("anecdote_report_count") + 1
    rated_anecdote_ids = data.get("rated_anecdote_ids", [])

    rated_anecdote_ids.append(anecdote_id)
    await RateDAO.add(
        session_with_commit,
        values=RateModel(anecdote_id=anecdote_id, user_id=user_id, rating=None),
    )

    await AnecdoteDAO.update(
        session_with_commit,
        values=AnecdoteUpdate(report_count=anecdote_report_count),
        filters=AnecdoteFilter(id=anecdote_id),
    )

    await callback.message.edit_reply_markup(reply_markup=reported_anecdote_kb())

    await send_next_anecdote(
        session_without_commit, state, rated_anecdote_ids, user_id, callback.message
    )


@anecdote_router.callback_query(F.data == "pass")
async def pass_callback(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
