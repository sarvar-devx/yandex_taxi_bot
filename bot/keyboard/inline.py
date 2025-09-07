"""
photo
f'<a href="">{driver.user.first_name}</a> Sizning malumotlaringiz\n\nIsm: {driver.user.first_name} \nFamiliya: {driver.user.last_name} \nTel: <a href="tel:+998{driver.user.phone_number}">+998{driver.user.phone_number}</a> \nMashina rusumi: {driver.car_brand} \nMashina raqami: {driver.car_number}'

inline button
[malumotni tasdiqlayman admin korib chiqishi uchun] [yoq men driverlikdan bosh tortaman]

"""
from aiogram.types import InlineKeyboardButton
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database import Driver


class RequestDrivingButtons:
    CONFIRM = InlineKeyboardButton(text="✅ Ha men taxi bo'lmoqchiman 🚖", callback_data="confirm_driving")
    REJECTION = InlineKeyboardButton(text="❌ Rad etish", callback_data="reject_driving")

    @staticmethod
    def get_markup():
        return InlineKeyboardMarkup(inline_keyboard=[
            [RequestDrivingButtons.CONFIRM],
            [RequestDrivingButtons.REJECTION]
        ])


class DriverInfoInlineKeyboardButtons:
    CHANGE_CAR_BRAND = InlineKeyboardButton(text="Mashina brendini o'zgartirish", callback_data="change_car_brand")
    CHANGE_CAR_NUMBER = InlineKeyboardButton(text="Mashina raqamini o'zgartirish", callback_data="change_car_number")
    CHANGE_LICENSE_TERM = InlineKeyboardButton(text="Litsenziyani o'zgartirish", callback_data="change_license_term")
    CHANGE_IMAGE = InlineKeyboardButton(text="Haydovchi rasmini ozgartirish", callback_data="change_image")

    @staticmethod
    def get_markup():
        return InlineKeyboardMarkup(inline_keyboard=[
            [DriverInfoInlineKeyboardButtons.CHANGE_CAR_NUMBER],
            [DriverInfoInlineKeyboardButtons.CHANGE_CAR_BRAND],
            [DriverInfoInlineKeyboardButtons.CHANGE_LICENSE_TERM],
            [DriverInfoInlineKeyboardButtons.CHANGE_IMAGE],
        ])


def user_order_type():
    ikb = InlineKeyboardBuilder()
    for car in Driver.CarType:
        ikb.add(
            InlineKeyboardButton(
                text=car.value.capitalize(),
                callback_data=car.value
            )
        )
    return ikb.as_markup()


def make_inline_keyboard(buttons: list[tuple[str, str]], row_width: int = 2):
    ikb = InlineKeyboardBuilder()
    for text, data in buttons:
        ikb.add(InlineKeyboardButton(text=text, callback_data=data))
    ikb.adjust(row_width)
    return ikb.as_markup()

# ISHLATILISHI

# driver_offer_kb = make_inline_keyboard([
#     ("✅ Qabul qilaman", "driver_accept"),
#     ("❌ Rad etaman", "driver_decline")
# ])