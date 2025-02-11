from aiogram.utils.keyboard import InlineKeyboardBuilder  
from aiogram.filters.callback_data import CallbackData
from typing import Optional


class GiveStarsCallbackFactory(CallbackData, prefix="give"):
    action: str
    value: Optional[int] = None
  

def give_stars_kb():  
    builder = InlineKeyboardBuilder()  
    builder.button(text=f"30 ⭐️", callback_data=GiveStarsCallbackFactory(action="stars", value=30))
    builder.button(text=f"50 ⭐️", callback_data=GiveStarsCallbackFactory(action="stars", value=50)) 
    builder.button(text=f"100 ⭐️", callback_data=GiveStarsCallbackFactory(action="stars", value=100))   
    builder.button(text="Назад", callback_data="back")
    builder.adjust(1, 1, 1)
    return builder.as_markup()