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
    ORDER_CANCEL = "Buyurtmani bekor qilish ❌"


class DriverButtons:
    GO = "Boshlash"
    START_WORK = "Ishni boshlash"
    FINISH_WORK = "Ishni tugatish"


class AdminButtons:
    DRIVER_CANDIDATES = "🚖Taxistlikga nomzodlar 👥"
    NEW_CAR_TYPE = "Yangi mashina toifasini qo'shish"


def main_keyboard_btn(is_driver=False) -> ReplyKeyboardBuilder:
    main_keyboard = ReplyKeyboardBuilder()
    if is_driver:
        main_keyboard.row(KeyboardButton(text=DriverButtons.GO))
    else:
        main_keyboard.row(KeyboardButton(text=UserButtons.ORDER_TAXI))
        main_keyboard.row(KeyboardButton(text=UserButtons.BECOME_DRIVER))

    main_keyboard.row(KeyboardButton(text=UserButtons.OPERATOR))
    main_keyboard.row(KeyboardButton(text=UserButtons.ORDER_HISTORY))
    main_keyboard.adjust(2, repeat=True)
    return main_keyboard


def admin_keyboard_btn() -> ReplyKeyboardMarkup:
    admin_keyboard = main_keyboard_btn()
    admin_keyboard.row(KeyboardButton(text=AdminButtons.DRIVER_CANDIDATES))
    admin_keyboard.row(KeyboardButton(text=AdminButtons.CAR_TYPES))
    admin_keyboard.adjust(2, repeat=True)
    admin_keyboard = admin_keyboard.as_markup(resize_keyboard=True)
    for row in admin_keyboard.keyboard:
        row[:] = [btn for btn in row if btn.text != UserButtons.BECOME_DRIVER]
    return admin_keyboard


def driver_keyboard_btn() -> ReplyKeyboardBuilder:
    driver_keyboard = ReplyKeyboardBuilder()
    driver_keyboard.row(KeyboardButton(text=DriverButtons.START_WORK, request_location=True))
    driver_keyboard.row(KeyboardButton(text=DriverButtons.FINISH_WORK))
    return driver_keyboard


def driver_finish_btn():
    keyboard = ReplyKeyboardBuilder()
    keyboard.row(KeyboardButton(text=DriverButtons.FINISH_WORK))
    return keyboard.as_markup(resize_keyboard=True)


phone_number_rkb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text='📞 Telefon raqamni yuborish', request_contact=True)]], resize_keyboard=True)

back_button_markup = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=UserButtons.BACK)]], resize_keyboard=True)


def get_location():
    rkb = ReplyKeyboardBuilder()
    rkb.add(KeyboardButton(text="Manzilni yuborish 📍", request_location=True))
    return rkb.as_markup(resize_keyboard=True)


def order_cancelled(user_id: int):
    rkb = ReplyKeyboardBuilder()
    rkb.add(KeyboardButton(text=f"{UserButtons.ORDER_CANCEL}"))
    return rkb.as_markup(resize_keyboard=True)
