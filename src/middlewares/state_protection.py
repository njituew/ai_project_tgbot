from aiogram import BaseMiddleware
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from src.registration import RegistrationStates
from src.survey_for_training import TrainingStates
from src.my_profile import UpdateProfile
from src.my_statistics import StatisticsState


class StateProtectionMiddleware(BaseMiddleware):
    """
    Middleware для проверки содержания сообщений во время загрузок/ожидания сообщений.
    """
    async def __call__(self, handler, event, data: dict):
        fsm_context: FSMContext = data.get("state")
        if fsm_context:
            state = await fsm_context.get_state()

            if state in [
                RegistrationStates.waiting_for_name,
                RegistrationStates.waiting_for_gender,
                RegistrationStates.waiting_for_age,
                RegistrationStates.waiting_for_height,
                RegistrationStates.waiting_for_weight,
            ]:
                if isinstance(event, Message) and event.text.startswith("/"):
                    await event.answer("Вы не завершили регистрацию. Пожалуйста, завершите её, чтобы продолжить.")
                    return
                return await handler(event, data)
            
            button_texts = [
                "Создать тренировку 🏋️‍♂️", "Мой план 📋", "Библиотека упражнений 📚",
                "Напоминания ⏰", "Мой профиль 👤", "Моя статистика 📈", "Опрос после тренировки 💬"
            ]

            cmds_without_ai_way = [
                "Библиотека упражнений 📚", "/exercises",
                "Мой профиль 👤", "/commands", "/my_profile", "/update_profile", "/start", "/menu"
            ]
            
            if state == TrainingStates.waiting_for_wishes:
                if isinstance(event, Message) and (event.text.startswith("/") or event.text in button_texts):
                    await event.answer("Вы не завершили опрос. Пожалуйста, завершите его, чтобы продолжить.")
                    return
                return await handler(event, data)
            
            if state in [TrainingStates.creating_training_plan, StatisticsState.creating_statistics]:
                if isinstance(event, Message) and not event.text in cmds_without_ai_way:
                    await event.answer("Пожалуйста, дождитесь окончания генерации ответа.")
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
            
        return await handler(event, data)