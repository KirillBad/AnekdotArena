from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.fsm.context import FSMContext
from admins.kbs import admin_panel_kb, report_actions_kb, back_to_admin_panel_kb, deleted_anecdote_kb
from admins.states import AdminStates
from anecdotes.dao import AnecdoteDAO
from anecdotes.schemas import AnecdoteFilter

admin_router = Router()

@admin_router.callback_query(F.data == "admin_panel")
async def show_admin_panel(callback: CallbackQuery):
    await callback.message.edit_text(text="🚔 Админ панель 🚔", reply_markup=admin_panel_kb())

@admin_router.callback_query(F.data == "show_reports")
async def show_admin_panel(callback: CallbackQuery, state: FSMContext, session_without_commit: AsyncSession):
    await callback.answer()

    await state.set_state(AdminStates.watching_reports)

    anecdotes = await AnecdoteDAO.find_all(session_without_commit, order_by="report_count")
    if not anecdotes:
        await callback.message.edit_text("Нет анекдотов с репортами", reply_markup=back_to_admin_panel_kb())
        return
    
    await state.update_data(
        anecdote_ids=[anecdote.id for anecdote in anecdotes],
        current_index=0
    )

    await show_report(callback.message, state, session_without_commit)   

@admin_router.callback_query(F.data == "delete_anecdote")
async def delete_anecdote(callback: CallbackQuery, state: FSMContext, session_with_commit: AsyncSession):
    data = await state.get_data()
    anecdote_ids = data.get("anecdote_ids", [])
    current_index = data.get("current_index", 0)
    print(anecdote_ids[current_index])

    await AnecdoteDAO.delete(session_with_commit, AnecdoteFilter(id=anecdote_ids[current_index]))
    await callback.message.edit_reply_markup(reply_markup=deleted_anecdote_kb())

    await state.update_data(
        current_index=current_index + 1
    )

    await show_report(callback.message, state, session_with_commit)

async def show_report(message: Message, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    anecdote_ids = data.get("anecdote_ids", [])
    current_index = data.get("current_index", 0)

    if not anecdote_ids or current_index >= len(anecdote_ids):
        await message.edit_text("Все анекдоты просмотрены", reply_markup=back_to_admin_panel_kb())
        return

    anecdote = await AnecdoteDAO.find_one_or_none_by_id(anecdote_ids[current_index], session)
    if not anecdote:
        return

    text = (
        f"{anecdote.content}\n\n"
        f"id анекдота #{anecdote.id}\n"
        f"Количество репортов: {anecdote.report_count}"
    )

    await message.answer(
        text=text,
        reply_markup=report_actions_kb()
    )
