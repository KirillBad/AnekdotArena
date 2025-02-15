from users.dao import UserDAO
from users.kbs import main_user_kb
from users.schemas import TelegramIDModel, UserModel
from anecdotes.dao import RateDAO
from anecdotes.schemas import RateModelUserId
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession
from payments.dao import DonationDAO


async def get_start_text(message: Message, session: AsyncSession) -> tuple[str, dict]:
    user_info = await UserDAO.find_one_or_none(
        session=session, filters=TelegramIDModel(telegram_id=message.from_user.id)
    )

    total_donation = await DonationDAO.sum_amount(session)

    if not user_info:
        values = UserModel(
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
        )

        user_info = await UserDAO.add(session=session, values=values)

    rates = await RateDAO.count(session, filters=RateModelUserId(user_id=user_info.id))

    text = f"⚔️ Добро пожаловать на <b>Анекдот Арену</b> 🛡️\n\n🎁 Пиши шутки и зарабатывай ⭐\n\n💰 Призовой фонд: <b>{total_donation}</b> ⭐️\n\n📝 Оценено анекдотов: <b>{rates}</b> 🔎"
    kb = main_user_kb(message.from_user.id)

    return text, kb
