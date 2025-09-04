from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


class UserButtons:
    ORDER_TAXI = "🚕 Taxi buyurtma qilish"
    OPERATOR = "📞 Operator"
    CHANGE_FIRST_NAME = "✍ Ismni o'zgartirish"
    CHANGE_LAST_NAME = "✍ Familiyani o'zgartirish"
    BECOME_DRIVER = "🚖 Haydovchi bo'lish"
    BACK = "🔙 Orqaga"
    ORDER_HISTORY = "📝 Buyurtmalar tarixi"


class DriverButtons:
    START_DRIVE = "Ishni boshlash"
    END_DRIVE = "Ishni tugatish"
    CHANGE_DRIVE_NAME = "Ismni o'zgartirish"
    CHANGE_DRIVE_CAR_NAME = "Mashina nomini o'zgartirish"
    CHANGE_DRIVE_CAR_NUM = "Mashina raqamini o'zgartirish"
    CHANGE_DRIVE_LICENSE = "Litsenziyani o'zgartirish"
    CHANGE_DRIVE_IMAGE = "Haydovchi rasmini ozgartirish"


def main_keyboard_btn(**kwargs) -> ReplyKeyboardBuilder:
    main_keyboard = ReplyKeyboardBuilder()
    main_keyboard.row(KeyboardButton(text=UserButtons.ORDER_TAXI, **kwargs))
    main_keyboard.row(KeyboardButton(text=UserButtons.OPERATOR, **kwargs))
    main_keyboard.row(KeyboardButton(text=UserButtons.ORDER_HISTORY, **kwargs))
    main_keyboard.adjust(2, repeat=True)
    return main_keyboard


phone_number_rkb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text='📞 Telefon raqamni yuborish', request_contact=True)]], resize_keyboard=True)
