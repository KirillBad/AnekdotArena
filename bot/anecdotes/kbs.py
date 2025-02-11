from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import Optional
from aiogram.filters.callback_data import CallbackData


class RateCallbackFactory(CallbackData, prefix="rate"):
    action: str
    value: Optional[int] = None


def back_to_start_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text=" Назад", callback_data="start")
    kb.adjust(1)
    return kb.as_markup()


def rate_anecdote_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="1️⃣", callback_data=RateCallbackFactory(action="rate", value=1))
    kb.button(text="2️⃣", callback_data=RateCallbackFactory(action="rate", value=2))
    kb.button(text="3️⃣", callback_data=RateCallbackFactory(action="rate", value=3))
    kb.button(text="4️⃣", callback_data=RateCallbackFactory(action="rate", value=4))
    kb.button(text="5️⃣", callback_data=RateCallbackFactory(action="rate", value=5)),
    kb.button(text="Похвалить звездой ⭐", callback_data="select_stars")
    kb.button(text="Назад", callback_data="start")
    kb.adjust(5, 1, 1)
    return kb.as_markup()


def rated_anecdote_kb(value: int) -> InlineKeyboardMarkup:
    number_emojis = {1: "1️⃣", 2: "2️⃣", 3: "3️⃣", 4: "4️⃣", 5: "5️⃣"}
    kb = InlineKeyboardBuilder()
    kb.button(text=f" Ваша оценка: {number_emojis[value]}", callback_data="pass")
    kb.adjust(1)
    return kb.as_markup()


def stars_payment_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="Назад", callback_data="start")
    kb.adjust(1)
    return kb.as_markup()
