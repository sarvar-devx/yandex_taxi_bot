from aiogram.filters import Filter
from aiogram.types import Message

from database import User, Driver


class IsAdmin(Filter):

    async def __call__(self, message: Message) -> bool:
        user = await User.get(message.from_user.id)
        return user.is_admin


class IsDriver(Filter):

    async def __call__(self, message: Message) -> bool:
        driver = await Driver.get(message.from_user.id)
        return True if driver else False


class IsCustomer(Filter):

    async def __call__(self, message: Message) -> bool:
        user = await Driver.get(message.from_user.id)
        return True if not user else False