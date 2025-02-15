from aiogram.types import Message
from admins.kbs import back_to_admin_panel_kb, report_actions_kb
from anecdotes.dao import AnecdoteDAO
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.fsm.context import FSMContext


async def show_report(message: Message, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    anecdote_ids = data.get("anecdote_ids", [])
    current_index = data.get("current_index", 0)

    if not anecdote_ids or current_index >= len(anecdote_ids):
        await message.answer(
            "Все анекдоты просмотрены", reply_markup=back_to_admin_panel_kb()
        )
        return

    anecdote = await AnecdoteDAO.find_one_or_none_by_id(
        anecdote_ids[current_index], session
    )
    if not anecdote:
        return

    text = (
        f"{anecdote.content}\n\n"
        f"id анекдота #{anecdote.id}\n"
        f"Количество репортов: {anecdote.report_count}"
    )

    await message.answer(text=text, reply_markup=report_actions_kb())
