import pandas as pd

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery

from src.registration import EXCEL_FILE


async def check_registered_boolean(user_id: str) -> bool:
    df = pd.read_excel(EXCEL_FILE)
    is_registered = not df[df["ID"] == user_id].empty
    
    return is_registered


class AuthorizationMiddleware(BaseMiddleware):
    """
    Middleware для проверки, зарегистрирован ли пользователь,
    с использованием кэша для оптимизации.
    """
    async def __call__(self, handler, event, data: dict):
        if isinstance(event, Message):
            user_id = event.from_user.id
            if not event.text:
                await data['bot'].send_message(user_id, "Пожалуйста, пишите текстовые сообщения. Я не могу обрабатывать другие типы сообщений.")
                return
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id
        else:
            user_id = None
            
        if not user_id:
            return await handler(event, data)

        if isinstance(event, Message) and event.text == "/start":
            return await handler(event, data)
                
        if not await check_registered_boolean(user_id):
            text = "Вы не зарегистрированы. Пожалуйста, зарегистрируйтесь, чтобы пользоваться всеми функциями бота.\n\n/start - начать работу с ботом"
            if isinstance(event, Message):
                await event.answer(text)
            elif isinstance(event, CallbackQuery):
                await event.message.answer(text)
            return

        return await handler(event, data)
