from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from src.registration import RegistrationStates, EXCEL_FILE
import pandas as pd


async def check_registered_boolean(user_id: str) -> bool:
    df = pd.read_excel(EXCEL_FILE)
    user = df[df["ID"] == user_id]
    return not user.empty


class RegistrationMiddleware(BaseMiddleware):
    """
    Middleware для проверки, зарегистрирован ли пользователь,
    с корректной обработкой команд и текстовых сообщений в процессе регистрации.
    """
    async def __call__(self, handler, event, data: dict):
        user_id = event.from_user.id if isinstance(event, (Message, CallbackQuery)) else None

        if not user_id:
            return await handler(event, data)

        # Пропускаем обработку команды /start
        if isinstance(event, Message) and event.text == "/start":
            return await handler(event, data)

        # Проверяем состояние FSM
        fsm_context: FSMContext = data.get("state")
        if fsm_context:
            state = await fsm_context.get_state()
            # Если пользователь в процессе регистрации, различаем команды и текст
            if state in [
                RegistrationStates.waiting_for_name,
                RegistrationStates.waiting_for_age,
                RegistrationStates.waiting_for_height,
                RegistrationStates.waiting_for_weight,
            ]:
                # Проверяем, является ли сообщение командой (начинается с '/')
                if isinstance(event, Message) and event.text.startswith("/"):
                    await event.answer("Вы не завершили регистрацию. Пожалуйста, завершите её, чтобы продолжить.")
                    return  # Прерываем обработку команды
                return await handler(event, data)  # Пропускаем текстовые сообщения

        # Проверяем регистрацию пользователя
        if not await check_registered_boolean(user_id):
            if isinstance(event, Message):
                await event.answer("Вы не зарегистрированы. Пожалуйста, зарегистрируйтесь, чтобы пользоваться всеми функциями бота.")
            elif isinstance(event, CallbackQuery):
                await event.message.answer("Вы не зарегистрированы. Пожалуйста, зарегистрируйтесь, чтобы пользоваться всеми функциями бота.")
            return  # Прерываем обработку, если пользователь не зарегистрирован

        # Если пользователь зарегистрирован, продолжаем обработку
        return await handler(event, data)