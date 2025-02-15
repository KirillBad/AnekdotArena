from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import Optional
from aiogram.filters.callback_data import CallbackData


class RateCallbackFactory(CallbackData, prefix="rate"):
    action: str
    value: Optional[int] = None


class PaginationCallbackFactory(CallbackData, prefix="pagination"):
    action: str
    page: int


def back_to_start_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="↩️ Назад", callback_data="start")
    kb.adjust(1)
    return kb.as_markup()


def rate_anecdote_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="1️⃣", callback_data=RateCallbackFactory(action="rate", value=1))
    kb.button(text="2️⃣", callback_data=RateCallbackFactory(action="rate", value=2))
    kb.button(text="3️⃣", callback_data=RateCallbackFactory(action="rate", value=3))
    kb.button(text="4️⃣", callback_data=RateCallbackFactory(action="rate", value=4))
    kb.button(text="5️⃣", callback_data=RateCallbackFactory(action="rate", value=5)),
    kb.button(text="Отправить подарок автору 🎁", callback_data="select_gift")
    kb.button(text="↩️ Назад", callback_data="start")
    kb.button(text="🚨 Пожаловаться", callback_data="report_anecdote")
    kb.adjust(5, 1, 2)
    return kb.as_markup()


def rated_anecdote_kb(value: int) -> InlineKeyboardMarkup:
    number_emojis = {1: "1️⃣", 2: "2️⃣", 3: "3️⃣", 4: "4️⃣", 5: "5️⃣"}
    kb = InlineKeyboardBuilder()
    kb.button(text=f" Ваша оценка: {number_emojis[value]}", callback_data="pass")
    kb.adjust(1)
    return kb.as_markup()


def reported_anecdote_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="🚨 Жалоба отправлена", callback_data="pass")
    kb.adjust(1)
    return kb.as_markup()


def pagination_anecdotes_kb(
    current_page: int, total_pages: int, source: str
) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    button_counter = 1
    if current_page > 1:
        kb.button(
            text="⬅️",
            callback_data=PaginationCallbackFactory(
                action="select_page", page=current_page - 1
            ),
        )
        button_counter += 1

    page_emoji = {1: "🥇", 2: "🥈", 3: "🥉"}.get(current_page, "📄")
    kb.button(text=f"{page_emoji} {current_page}/{total_pages}", callback_data="pass")

    if current_page < total_pages:
        kb.button(
            text="➡️",
            callback_data=PaginationCallbackFactory(
                action="select_page", page=current_page + 1
            ),
        )
        button_counter += 1

    if source == "top_anecdotes":
        kb.button(text="Отправить подарок автору 🎁", callback_data="select_gift")
        kb.button(text="↩️ Назад", callback_data="start")
        kb.adjust(button_counter, 1, 1)
    elif source == "my_anecdotes":
        kb.button(text="↩️ Назад", callback_data="start")
        kb.adjust(button_counter, 1)

    return kb.as_markup()
