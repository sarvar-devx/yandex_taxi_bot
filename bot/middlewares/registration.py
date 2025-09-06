from aiogram import BaseMiddleware
from aiogram.types import Message
from aiogram.types.update import Update

from bot.handlers.register import become_to_driver
from database import User, Driver
from utils.services import send_first_name


class RegistrationMiddleware(BaseMiddleware):
    async def __call__(self, handler, update: Update, data):
        message = update.event
        if not isinstance(message, Message):
            message = message.message

        user = await User.get(update.event.from_user.id)
        if not user:
            user = await User.create(id=update.event.from_user.id, username=update.event.from_user.username,
                                     first_name=update.event.from_user.first_name,
                                     last_name=update.event.from_user.last_name)

        if not user.phone_number and not await data['state'].get_state():
            await send_first_name(message, data['state'])
            return

        return await handler(update, data)



