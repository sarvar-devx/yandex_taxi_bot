"""
photo
f'<a href="">{driver.user.first_name}</a> Sizning malumotlaringiz\n\nIsm: {driver.user.first_name} \nFamiliya: {driver.user.last_name} \nTel: <a href="tel:+998{driver.user.phone_number}">+998{driver.user.phone_number}</a> \nMashina rusumi: {driver.car_brand} \nMashina raqami: {driver.car_number}'

inline button
[malumotni tasdiqlayman admin korib chiqishi uchun] [yoq men driverlikdan bosh tortaman]

"""
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


class RequestDrivingButtons:
    CONFIRM = InlineKeyboardButton(text="✅ Ha men taxi bo'lmoqchiman 🚖", callback_data="confirm_driving")
    REJECTION = InlineKeyboardButton(text="❌ Rad etish", callback_data="reject_driving")

    @staticmethod
    def get_markup():
        return InlineKeyboardMarkup(inline_keyboard=[
            [RequestDrivingButtons.CONFIRM],
            [RequestDrivingButtons.REJECTION]
        ])
