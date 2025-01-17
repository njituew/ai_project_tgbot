import asyncio

from aiogram import Bot, Dispatcher, F
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import CommandStart, Command

from src.default_commands import cmd_menu, cmd_start, handle_button_click, set_bot_commands
from src.registration import RegistrationStates, process_age, process_height, process_name, process_weight
from src.survey_for_training import start_survey, new_training, set_goal, set_level, set_location, TrainingSurvey
from src.my_plan import show_plan, plan_operation
from src.exercise_library import show_exercise_categories, handle_back_to_categories, handle_category_selection, handle_exercise_selection
from src.my_profile import show_profile_info
from src.middleware_registration import RegistrationMiddleware
from src.utils import get_bot_token
from src.reminders import show_reminders_menu, enable_notifications, disable_notifications, on_startup
from src.logging_middleware import LoggingMiddleware


'''
    Загрузка токена бота из файла .env
    В файле .env:
    BOT_TOKEN = ...
'''
TOKEN = get_bot_token()

# Инициализация бота и диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())


# Регистрация ручек
dp.message.middleware(RegistrationMiddleware())
dp.callback_query.middleware(RegistrationMiddleware())
dp.message.middleware(LoggingMiddleware())
dp.callback_query.middleware(LoggingMiddleware())

dp.message.register(cmd_start, CommandStart())  # команда /start
dp.message.register(process_name, RegistrationStates.waiting_for_name)
dp.message.register(process_age, RegistrationStates.waiting_for_age)
dp.message.register(process_height, RegistrationStates.waiting_for_height)
dp.message.register(process_weight, RegistrationStates.waiting_for_weight)

dp.message.register(cmd_menu, Command("menu"))  # команда /menu

dp.message.register(start_survey, F.text == "Создать тренировку 🏋️‍♂️")
dp.callback_query.register(new_training, TrainingSurvey.new_training)
dp.callback_query.register(set_goal, TrainingSurvey.goal)
dp.callback_query.register(set_level, TrainingSurvey.level)
dp.callback_query.register(set_location, TrainingSurvey.location)

dp.message.register(show_plan, F.text == "Мой план 📋")
dp.callback_query.register(plan_operation, F.data == "new_plan")
dp.callback_query.register(plan_operation, F.data == "remove_plan")

dp.message.register(show_exercise_categories, F.text == "Упражнения 📚")
dp.callback_query.register(handle_category_selection, F.data.startswith("category_"))
dp.callback_query.register(handle_exercise_selection, F.data.startswith("exercise_"))
dp.callback_query.register(handle_back_to_categories, F.data == "back_to_categories")

dp.message.register(show_reminders_menu, F.text == "Напоминания ⏰")
dp.callback_query.register(new_training, F.data == "new_training")
dp.callback_query.register(enable_notifications, F.data == "turn_on_reminder")
dp.callback_query.register(disable_notifications, F.data == "turn_off_reminder")

dp.message.register(show_profile_info, F.text == "Мой профиль 👤")

dp.message.register(handle_button_click)


# Запуск бота
async def main():
    await set_bot_commands(bot)
    await on_startup()
    await dp.start_polling(bot)


if __name__ == "__main__":
    print("Bot is running...")
    asyncio.run(main())
