from aiogram.filters import Filter
from aiogram.types import Message

from database import User, Driver


class IsAdmin(Filter):

    async def __call__(self, message: Message) -> bool:
        user = await User.get(message.from_user.id)
        return user.is_admin


class IsDriver(Filter):

    async def __call__(self, message: Message) -> bool:
        driver = await Driver.get_or_none(user_id=message.from_user.id)
        return driver is not None


class IsCustomer(Filter):

    async def __call__(self, message: Message) -> bool:
        user = await User.get(message.from_user.id)
        return user.driver_profile is None and not user.is_admin
