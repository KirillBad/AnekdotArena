from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config_reader import config


def main_user_kb(user_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="✍️ Написать анекдот", callback_data="write_anecdote")
    kb.button(text="💌 Оценить анекдот", callback_data="rate_anecdote")
    kb.button(text="🏆 Топ анекдотов", callback_data="top_anecdotes")
    kb.button(text="📂 Мои анекдоты", callback_data="my_anecdotes")
    kb.button(text="💸 Пополнить призовой фонд", callback_data="donate_to_prize_fund")
    if user_id in config.ADMIN_IDS:
        kb.button(text="⚙️ Админ панель", callback_data="admin_panel")
    kb.adjust(1)
    return kb.as_markup()


def contact_us_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="💬 Связаться с нами", callback_data="contact_us")
    return kb.as_markup()
