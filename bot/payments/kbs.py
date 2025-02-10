from aiogram.utils.keyboard import InlineKeyboardBuilder  
  
  
def give_stars_kb():  
    builder = InlineKeyboardBuilder()  
    builder.button(text=f"Оплатить 10 ⭐️", pay=True, callback_data="give_stars_10")  
  
    return builder.as_markup()