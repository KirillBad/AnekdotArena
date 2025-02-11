from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from anecdotes.utils import send_next_anecdote
from users.kbs import main_user_kb
from sqlalchemy.ext.asyncio import AsyncSession
from anecdotes.schemas import AnecdoteModel
from anecdotes.dao import AnecdoteDAO, RateDAO
from users.dao import UserDAO
from users.schemas import TelegramIDModel
from pydantic import ValidationError
from anecdotes.states import AnecdoteStates, RateStates
from anecdotes.kbs import RateCallbackFactory, rated_anecdote_kb, back_to_start_kb, top_anecdotes_kb, TopAnecdotesCallbackFactory
from anecdotes.schemas import RateModel, RateModelUserId

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
    message: Message, state: FSMContext, session_with_commit: AsyncSession
):
    text = message.text

    user = await UserDAO.find_one_or_none(
        session=session_with_commit,
        filters=TelegramIDModel(telegram_id=message.from_user.id),
    )

    try:
        values = AnecdoteModel(content=text, user_id=user.id)
        await AnecdoteDAO.add(session=session_with_commit, values=values)
        await state.clear()

        await message.answer(
            "✅ Ваш анекдот успешно сохранен!", reply_markup=main_user_kb(user.id)
        )
    except ValidationError as e:
        error_message = "❌ Ошибка:\n"
        if "string_too_short" in str(e):
            error_message += "Текст анекдота должен содержать минимум 5 символов!"
        elif "string_too_long" in str(e):
            error_message += "Текст анекдота не должен превышать 1000 символов!"
        else:
            error_message += "Неверный формат данных!"

        error_message += "\n\nПопробуйте еще раз"

        await message.answer(error_message, reply_markup=back_to_start_kb())


@anecdote_router.callback_query(F.data == "rate_anecdote")
async def rate_anecdote(
    callback: CallbackQuery, state: FSMContext, session_without_commit: AsyncSession
):
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
        session_with_commit, state, rated_anecdote_ids, user_id, callback.message
    )

@anecdote_router.callback_query(F.data == "top_anecdotes")
async def top_anecdotes(callback: CallbackQuery, state: FSMContext, session_without_commit: AsyncSession):
    await state.set_state(RateStates.watching_top_anecdotes)
    top_rates = await RateDAO.get_top_anecdotes(session_without_commit)
    await state.update_data(top_rates=top_rates, anecdote_author_id=top_rates[0].user_id, page=1)
    await callback.message.edit_text(
        text=f"{top_rates[0].content}",
        reply_markup=top_anecdotes_kb(1, 10),
    )

@anecdote_router.callback_query(TopAnecdotesCallbackFactory.filter(F.action == "select_page"))
async def process_next_top_anecdotes(callback: CallbackQuery, callback_data: TopAnecdotesCallbackFactory, state: FSMContext):
    data = await state.get_data()
    top_rates = data.get("top_rates")
    await state.update_data(anecdote_author_id=top_rates[callback_data.page - 1].user_id, page=callback_data.page)
    await callback.message.edit_text(
        text=f"{top_rates[callback_data.page - 1].content}",
        reply_markup=top_anecdotes_kb(callback_data.page, 10),
    )
