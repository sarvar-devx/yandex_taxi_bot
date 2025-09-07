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
