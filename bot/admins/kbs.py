from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def admin_panel_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="🚨 Жалобы", callback_data="show_reports")
    kb.button(text="↩️ Назад", callback_data="start")
    kb.adjust(1)
    return kb.as_markup()


def report_actions_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Аннулировать жалобы", callback_data="cancel_reports")
    kb.button(text="🚫 Удалить анекдот", callback_data="delete_anecdote")
    kb.button(text="↩️ Назад", callback_data="admin_panel")
    kb.adjust(1)
    return kb.as_markup()


def back_to_admin_panel_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="↩️ Назад", callback_data="admin_panel")
    kb.adjust(1)
    return kb.as_markup()


def deleted_anecdote_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="🚫 Анекдот удален", callback_data="pass")
    kb.adjust(1)
    return kb.as_markup()


def canceled_reports_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Жалобы аннулированы", callback_data="pass")
    kb.adjust(1)
    return kb.as_markup()
