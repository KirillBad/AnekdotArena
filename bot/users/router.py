from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from users.dao import UserDAO
from users.kbs import main_user_kb
from users.schemas import TelegramIDModel, UserModel
from anecdotes.dao import RateDAO
from anecdotes.schemas import RateModelUserId


user_router = Router()

async def get_start_text(message: Message, session: AsyncSession) -> tuple[str, dict]:
    """Получает текст и параметры для стартового сообщения"""
    user_info = await UserDAO.find_one_or_none(
        session=session, filters=TelegramIDModel(telegram_id=message.from_user.id)
    )

    if not user_info:
        values = UserModel(
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
        )

        user_info = await UserDAO.add(session=session, values=values)

    rates = await RateDAO.count(session, filters=RateModelUserId(user_id=user_info.id))
    
    text = f"⚔️ Добро пожаловать на <b>Анекдот Арену</b> 🛡️\n\nПиши шутки и зарабатывай ⭐\n\nОценено анекдотов: <b>{rates}</b>"
    kb = main_user_kb(message.from_user.id)

    return text, kb

@user_router.message(CommandStart())
async def cmd_start(message: Message, session_with_commit: AsyncSession):
    text, kb = await get_start_text(
        message, 
        session_with_commit
    )
    return await message.answer(text, reply_markup=kb)


@user_router.callback_query(F.data == "start")
async def back_to_start(call: CallbackQuery,  session_without_commit: AsyncSession):
    text, kb = await get_start_text(
        call, 
        session_without_commit
    )
    await call.message.edit_text(text, reply_markup=kb)
