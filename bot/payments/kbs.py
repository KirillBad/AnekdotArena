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
    builder.button(text=f"🧸 за 15 ⭐️", callback_data=SendGiftCallbackFactory(action="gift", value=15, gift_emoji="🧸", gift_id="5170233102089322756"))
    builder.button(text=f"🎁 за 15 ⭐️", callback_data=SendGiftCallbackFactory(action="gift", value=1, gift_emoji="🎁", gift_id="5168103777563050263")) 
    builder.button(text="Назад", callback_data="back")
    builder.adjust(1, 1, 1)
    return builder.as_markup()
