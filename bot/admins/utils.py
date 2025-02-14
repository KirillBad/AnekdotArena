from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from anecdotes.dao import AnecdoteDAO
from anecdotes.states import RateStates
from anecdotes.kbs import rate_anecdote_kb, back_to_start_kb
from users.kbs import main_user_kb


async def send_next_report(
    session: AsyncSession,
    state: FSMContext,
    reports_ids: list[int],
    user_id: int,
    message,
) -> bool:
    report = await AnecdoteDAO.find_one_random_not_in(
        session, exclude_ids=reports_ids, user_id=user_id
    )

    if anecdote:
        await state.set_state(RateStates.waiting_for_rate)
        await state.update_data(
            anecdote_id=anecdote.id,
            anecdote_content=anecdote.content,
            anecdote_author_id=anecdote.user_id,
            anecdote_report_count=anecdote.report_count,
            user_id=user_id,
            rated_anecdote_ids=rated_anecdote_ids,
        )
        await message.answer(text=anecdote.content, reply_markup=rate_anecdote_kb())
    else:
        await state.clear()
        await message.answer(
            text="Вы оценили все анекдоты😔\n\nВозвращайтесь позже ☺️", reply_markup=back_to_start_kb()
        )
