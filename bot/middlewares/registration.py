from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message
from aiogram.types.update import Update

from database import User
from database.base import db, AsyncSession
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


class DbSessionMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[Any, Dict[str, Any]], Awaitable[Any]],
            event: Any,
            data: Dict[str, Any]
    ) -> Any:
        async with db._engine.begin() as conn:  # engine orqali ishlash emas, balki session ochish kerak
            async with db._engine.connect() as connection:
                async with AsyncSession(bind=connection) as session:
                    data["session"] = session
                    return await handler(event, data)
