from aiogram.types import InlineKeyboardButton
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database import Driver


def driver_order_keyboard(order_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Qabul qilish", callback_data=f"accept_order:{order_id}"),
                InlineKeyboardButton(text="❌ Rad etish", callback_data=f"reject_order:{order_id}")
            ]
        ]
    )


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


def drivers_list(drivers: list[Driver]) -> InlineKeyboardMarkup:
    ikb = InlineKeyboardBuilder()

    for driver in drivers:
        ikb.row(InlineKeyboardButton(text=driver.user.first_name, callback_data=F"driver_id: {driver.user_id}"))
    ikb.adjust(2)
    return ikb.as_markup()


def inline_car_types_buttons(driver_id, car_types) -> InlineKeyboardMarkup:
    ikb = InlineKeyboardBuilder()
    for car_type in car_types:
        ikb.row(InlineKeyboardButton(text=car_type.name.title(),
                                     callback_data=f"driver_car_type {car_type.name} {driver_id}"))
    ikb.adjust(4)
    return ikb.as_markup()


def user_order_type(car_types):
    ikb = InlineKeyboardBuilder()
    for car_type in car_types:
        ikb.add(
            InlineKeyboardButton(
                text=car_type.name.capitalize(),
                callback_data=car_type.name
            )
        )
    return ikb.as_markup()


def make_inline_keyboard(buttons: list[tuple[str, str]], row_width: int = 2):
    ikb = InlineKeyboardBuilder()
    for text, data in buttons:
        ikb.add(InlineKeyboardButton(text=text, callback_data=data))
    ikb.adjust(row_width)
    return ikb.as_markup()


def car_types_list_buttons(car_types) -> InlineKeyboardMarkup:
    ikb = InlineKeyboardBuilder()

    for car_type in car_types:
        ikb.row(InlineKeyboardButton(text=car_type.name.upper(), callback_data=f"car_type_info_{car_type.id}"))

    ikb.adjust(2)
    return ikb.as_markup()
