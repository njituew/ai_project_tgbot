import asyncio

from aiogram import Bot, Dispatcher, F
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import CommandStart, Command

from src.default_commands import cmd_menu, cmd_start, cmd_commands, simple_message, set_bot_commands
from src.registration import RegistrationStates, process_name, process_gender, process_age, process_height, process_weight
from src.survey_for_training import *
from src.my_plan import show_plan
from src.exercise_library import show_exercise_categories, handle_back_to_categories, handle_category_selection, handle_exercise_selection
from src.my_profile import show_profile_info
from src.reminders import show_reminders_menu, enable_notifications, disable_notifications, on_startup
from src.middleware_registration import RegistrationMiddleware
from src.logging_middleware import LoggingMiddleware
from src.utils import get_bot_token
from src.workout_survey import open_workout_survey, some_exercises, defer_survey, without_exercises, all_exercises


'''
    Загрузка токена бота из файла .env
    В файле .env:
    BOT_TOKEN = ...
'''
TOKEN = get_bot_token()

# Инициализация бота и диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())


'''
Регистрация ручек
'''

# Middleware для регистрации
dp.message.middleware(RegistrationMiddleware())
dp.callback_query.middleware(RegistrationMiddleware())
dp.message.middleware(LoggingMiddleware())
dp.callback_query.middleware(LoggingMiddleware())

# Стандартные команды
dp.message.register(cmd_start, CommandStart())
dp.message.register(cmd_menu, Command("menu"))
dp.message.register(cmd_commands, Command("commands"))

# Регистрация пользователя
dp.message.register(process_name, RegistrationStates.waiting_for_name)
dp.callback_query.register(process_gender, RegistrationStates.waiting_for_gender)
dp.message.register(process_age, RegistrationStates.waiting_for_age)
dp.message.register(process_height, RegistrationStates.waiting_for_height)
dp.message.register(process_weight, RegistrationStates.waiting_for_weight)

# Создание тренировки
dp.message.register(start_survey, Command("generate_plan"))
dp.message.register(start_survey, F.text == "Создать тренировку 🏋️‍♂️")
dp.callback_query.register(new_training, F.data.startswith("survey_training_new"))
dp.callback_query.register(set_goal, F.data.startswith("goal_"))
dp.callback_query.register(set_level, F.data.startswith("level_"))
dp.callback_query.register(set_location, F.data.startswith("location_"))
dp.callback_query.register(set_wishes, TrainingStates.waiting_for_wishes)

# Мой план тренировок
dp.message.register(show_plan, Command("my_plan"))
dp.message.register(show_plan, F.text == "Мой план 📋")
dp.callback_query.register(new_training, F.data == "my_plan_new")
dp.callback_query.register(remove_training, F.data == "my_plan_remove")

# Библиотека упражнений
dp.message.register(show_exercise_categories, F.text == "Упражнения 📚")
dp.message.register(show_exercise_categories, Command("exercises"))
dp.callback_query.register(handle_category_selection, F.data.startswith("category_"))
dp.callback_query.register(handle_exercise_selection, F.data.startswith("exercise_"))
dp.callback_query.register(handle_back_to_categories, F.data == "back_to_categories")

# Напоминания
dp.message.register(show_reminders_menu, Command("reminder"))
dp.message.register(show_reminders_menu, F.text == "Напоминания ⏰")
dp.callback_query.register(new_training, F.data == "reminders_new_training")
dp.callback_query.register(enable_notifications, F.data == "turn_on_reminder")
dp.callback_query.register(disable_notifications, F.data == "turn_off_reminder")

# Мой профиль
dp.message.register(show_profile_info, Command("my_profile"))
dp.message.register(show_profile_info, F.text == "Мой профиль 👤")

# Опрос
dp.message.register(open_workout_survey, F.text == "Опрос💬")
dp.callback_query.register(all_exercises, F.data == "all_exercises_are_completed")
dp.callback_query.register(some_exercises, F.data == "some_exercises_are_completed")
dp.callback_query.register(without_exercises, F.data == "not_today")
dp.callback_query.register(defer_survey, F.data == "proceed_to_survey_later")

# Простое сообщение
dp.message.register(simple_message)


# Запуск бота
async def main():
    await set_bot_commands(bot)
    await on_startup()
    await dp.start_polling(bot)


if __name__ == "__main__":
    print("Bot is running...")
    asyncio.run(main())
