from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from src.registration import RegistrationStates, EXCEL_FILE
from src.survey_for_training import TrainingStates
from src.my_profile import UpdateProfile
import pandas as pd


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

        # Пропускаем обработку команды /start
        if isinstance(event, Message) and event.text == "/start":
            return await handler(event, data)

        # Проверяем состояние FSM
        fsm_context: FSMContext = data.get("state")
        if fsm_context:
            state = await fsm_context.get_state()
            # Если пользователь в процессе регистрации
            if state in [
                RegistrationStates.waiting_for_name,
                RegistrationStates.waiting_for_gender,
                RegistrationStates.waiting_for_age,
                RegistrationStates.waiting_for_height,
                RegistrationStates.waiting_for_weight,
            ]:
                if isinstance(event, Message) and event.text.startswith("/"):
                    await event.answer("Вы не завершили регистрацию. Пожалуйста, завершите её, чтобы продолжить.")
                    return  # Прерываем обработку команды
                return await handler(event, data)  # Пропускаем текстовые сообщения
            
            button_texts = [
                "Создать тренировку 🏋️‍♂️", "Мой план 📋", "Библиотека упражнений 📚",
                "Напоминания ⏰", "Мой профиль 👤", "Моя статистика 📈", "Опрос после тренировки 💬"
            ]
            
            if state == TrainingStates.waiting_for_wishes:
                if isinstance(event, Message) and (event.text.startswith("/") or event.text in button_texts):
                    await event.answer("Вы не завершили создание тренировки. Пожалуйста, завершите её, чтобы продолжить.")
                    return
                return await handler(event, data)
            
            if state == UpdateProfile.waiting_for_update_value:
                if isinstance(event, Message) and (event.text.startswith("/") or event.text in button_texts):
                    await event.answer("Вы не завершили обновление профиля. Пожалуйста, завершите его, чтобы продолжить.")
                    return
                return await handler(event, data)
            
            if state == UpdateProfile.waiting_for_bot_score:
                if isinstance(event, Message) and event.text.startswith("/"):
                    await event.answer("Вы не завершили оценку бота. Пожалуйста, завершите её, чтобы продолжить.")
                    return
                return await handler(event, data)
                

        # Проверяем регистрацию пользователя через кэш
        if not await check_registered_boolean(user_id):
            text = "Вы не зарегистрированы. Пожалуйста, зарегистрируйтесь, чтобы пользоваться всеми функциями бота.\n\n/start - начать работу с ботом"
            if isinstance(event, Message):
                await event.answer(text)
            elif isinstance(event, CallbackQuery):
                await event.message.answer(text)
            return  # Прерываем обработку, если пользователь не зарегистрирован

        # Если пользователь зарегистрирован, продолжаем обработку
        return await handler(event, data)
