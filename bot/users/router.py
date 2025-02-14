from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from users.utils import get_start_text
from aiogram.fsm.context import FSMContext

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
