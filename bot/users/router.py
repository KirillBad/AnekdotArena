from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from users.utils import get_start_text
from aiogram.fsm.context import FSMContext
from anecdotes.kbs import pagination_anecdotes_kb
from anecdotes.dao import AnecdoteDAO, RateDAO
from users.schemas import TelegramIDModel
from users.dao import UserDAO
from users.states import UserStates
from anecdotes.kbs import PaginationCallbackFactory, back_to_start_kb
from anecdotes.schemas import AnecdoteUserIdFilter

user_router = Router()


@user_router.message(CommandStart())
async def cmd_start(message: Message, session_with_commit: AsyncSession):
    text, kb = await get_start_text(message, session_with_commit)
    return await message.answer(text, reply_markup=kb)

@user_router.callback_query(F.data == "start")
async def back_to_start(callback: CallbackQuery, state: FSMContext, session_without_commit: AsyncSession):
    await state.clear()
    text, kb = await get_start_text(callback, session_without_commit)
    await callback.message.edit_text(text, reply_markup=kb)

@user_router.callback_query(F.data == "my_anecdotes")
async def my_anecdotes(callback: CallbackQuery, state: FSMContext, session_without_commit: AsyncSession):
    await state.set_state(UserStates.watching_my_anecdotes)

    user = await UserDAO.find_one_or_none(
        session=session_without_commit, filters=TelegramIDModel(telegram_id=callback.from_user.id)
    )

    my_anecdotes = await AnecdoteDAO.get_anecdotes_with_rating(session=session_without_commit, filters=AnecdoteUserIdFilter(user_id=user.id))

    if not my_anecdotes:
        await callback.message.edit_text("У вас пока нет анекдотов", reply_markup=back_to_start_kb())
        return

    await state.update_data(my_anecdotes=my_anecdotes)
    await callback.message.edit_text(f"{my_anecdotes[0].content}\n\n📈 Рейтинг: {my_anecdotes[0].avg_rating}", reply_markup=pagination_anecdotes_kb(1, len(my_anecdotes), "my_anecdotes"))

@user_router.callback_query(PaginationCallbackFactory.filter(F.action == "select_page"), UserStates.watching_my_anecdotes)
async def process_next_my_anecdotes(callback: CallbackQuery, callback_data: PaginationCallbackFactory, state: FSMContext):
    data = await state.get_data()
    my_anecdotes = data.get("my_anecdotes")
    await state.update_data(page=callback_data.page)
    await callback.message.edit_text(
        text=f"{my_anecdotes[callback_data.page - 1].content}\n\n📈 Рейтинг: {my_anecdotes[0].avg_rating}",
        reply_markup=pagination_anecdotes_kb(callback_data.page, len(my_anecdotes), "my_anecdotes"),
    )
