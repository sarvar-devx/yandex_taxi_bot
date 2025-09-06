from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from database import Driver


class UserButtons:
    ORDER_TAXI = "🚕 Taxi buyurtma qilish"
    OPERATOR = "📞 Operator"
    CHANGE_FIRST_NAME = "✍ Ismni o'zgartirish"
    CHANGE_LAST_NAME = "✍ Familiyani o'zgartirish"
    BECOME_DRIVER = "🚖 Haydovchi bo'lish"
    BACK = "🔙 Orqaga"
    ORDER_HISTORY = "📝 Buyurtmalar tarixi"


class DriverButtons:
    START_WORK = "Ishni boshlash"
    FINISH_WORK = "Ishni tugatish"
    CHANGE_CAR_BRAND = "Mashina brendini o'zgartirish"
    CHANGE_CAR_NUMBER = "Mashina raqamini o'zgartirish"
    CHANGE_LICENSE_TERM = "Litsenziyani o'zgartirish"
    CHANGE_IMAGE = "Haydovchi rasmini ozgartirish"


class AdminButtons:
    GET_CHAT_ID = "🆔 Chat ID ni ko‘rish"
    MANAGE_DRIVERS = "🚖 Haydovchilarni boshqarish"
    STATISTICS = "📊 Statistika"


def main_keyboard_btn() -> ReplyKeyboardBuilder:
    main_keyboard = ReplyKeyboardBuilder()
    main_keyboard.row(KeyboardButton(text=UserButtons.ORDER_TAXI))
    main_keyboard.row(KeyboardButton(text=UserButtons.OPERATOR))
    main_keyboard.row(KeyboardButton(text=UserButtons.ORDER_HISTORY))
    main_keyboard.adjust(2, repeat=True)
    return main_keyboard


def driver_info_keyboard_btn() -> ReplyKeyboardBuilder:
    driver_keyboard = ReplyKeyboardBuilder()
    driver_keyboard.row(KeyboardButton(text=UserButtons.CHANGE_FIRST_NAME))
    driver_keyboard.row(KeyboardButton(text=UserButtons.CHANGE_LAST_NAME))
    driver_keyboard.row(KeyboardButton(text=DriverButtons.CHANGE_IMAGE))
    driver_keyboard.row(KeyboardButton(text=DriverButtons.CHANGE_CAR_BRAND))
    driver_keyboard.row(KeyboardButton(text=DriverButtons.CHANGE_CAR_NUMBER))
    driver_keyboard.row(KeyboardButton(text=DriverButtons.CHANGE_LICENSE_TERM))
    driver_keyboard.row(KeyboardButton(text=UserButtons.BACK))
    driver_keyboard.adjust(2, repeat=True)
    return driver_keyboard


phone_number_rkb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text='📞 Telefon raqamni yuborish', request_contact=True)]], resize_keyboard=True)
