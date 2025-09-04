from aiogram.filters import Filter
from aiogram.types import Message

from config import conf


class IsAdminFilter(Filter):
    async def __call__(self, message: Message) -> bool:
        return message.from_user.id in conf.bot.get_admin_list
