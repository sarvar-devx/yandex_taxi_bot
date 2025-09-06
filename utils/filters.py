from aiogram.filters import Filter
from aiogram.types import Message

from config import conf
from database import User


class IsAdminFilter(Filter):
    async def __call__(self, message: Message) -> bool:
        user = await User.get(message.from_user.id)
        return user.is_admin
