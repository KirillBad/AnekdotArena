from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData
from typing import Optional


class SendGiftCallbackFactory(CallbackData, prefix="send"):
    action: str
    gift_emoji: str
    gift_id: str
    value: Optional[int] = None


def send_gift_kb():
    builder = InlineKeyboardBuilder()
    builder.button(
        text=f"🧸 за 25 ⭐️",
        callback_data=SendGiftCallbackFactory(
            action="gift", value=25, gift_emoji="🧸", gift_id="5170233102089322756"
        ),
    )
    builder.button(
        text=f"🎁 за 35 ⭐️",
        callback_data=SendGiftCallbackFactory(
            action="gift", value=35, gift_emoji="🎁", gift_id="5168103777563050263"
        ),
    )
    builder.button(
        text=f"🍾 за 60 ⭐️",
        callback_data=SendGiftCallbackFactory(
            action="gift", value=60, gift_emoji="🍾", gift_id="6028601630662853006"
        ),
    )
    builder.button(
        text=f"🏆 за 110 ⭐️",
        callback_data=SendGiftCallbackFactory(
            action="gift", value=110, gift_emoji="🏆", gift_id="5168043875654172773"
        ),
    )
    builder.button(text="↩️ Назад", callback_data="back")
    builder.adjust(2, 2, 1)
    return builder.as_markup()


def write_gift_text_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text="↪️ Без текста", callback_data="skip_text")
    builder.button(text="↩️ Назад", callback_data="back")
    builder.adjust(1, 1)
    return builder.as_markup()
