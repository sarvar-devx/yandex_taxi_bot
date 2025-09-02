from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


class UserButtons:
    ORDER_TAXI = "🚕 Taxi buyurtma qilish"
    OPERATOR = "📞 Operator"
    CHANGE_FIRST_NAME = "✍ Ismni o'zgartirish"
    CHANGE_LAST_NAME = "✍ Familiyani o'zgartirish"
    BACK = '🔙 Orqaga'
    ORDER_HISTORY = "📝 Buyurtmalar tarixi"


def main_keyboard_btn(**kwargs) -> ReplyKeyboardBuilder:
    main_keyboard = ReplyKeyboardBuilder()
    main_keyboard.row(KeyboardButton(text=UserButtons.ORDER_TAXI, **kwargs))
    main_keyboard.row(KeyboardButton(text=UserButtons.OPERATOR, **kwargs))
    main_keyboard.row(KeyboardButton(text=UserButtons.ORDER_HISTORY, **kwargs))
    main_keyboard.adjust(2, repeat=True)
    return main_keyboard


phone_number_rkb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text='📞 Telefon raqamni yuborish', request_contact=True)]], resize_keyboard=True)
