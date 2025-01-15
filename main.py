import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import CommandStart, Command
from src.registration import RegistrationStates, process_age, process_height, process_name, process_weight
from src.utils import get_bot_token
from src.default_commands import cmd_menu, cmd_start, handle_button_click, set_bot_commands
from src.survey_for_training import start_survey, new_training, set_goal, set_level, set_location, TrainingSurvey
from src.exercise_library import show_exercise_categories, handle_back_to_categories, handle_category_selection, handle_exercise_selection
from src.middleware_registration import RegistrationMiddleware

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

dp.message.register(cmd_start, CommandStart())  # команда /start
dp.message.register(cmd_menu, Command("menu"))  # команда /menu

dp.message.register(process_name, RegistrationStates.waiting_for_name)
dp.message.register(process_age, RegistrationStates.waiting_for_age)
dp.message.register(process_height, RegistrationStates.waiting_for_height)
dp.message.register(process_weight, RegistrationStates.waiting_for_weight)

dp.message.register(start_survey, F.text == "Создать тренировку 🏋️‍♂️")
dp.callback_query.register(new_training, TrainingSurvey.new_training)
dp.callback_query.register(set_goal, TrainingSurvey.goal)
dp.callback_query.register(set_level, TrainingSurvey.level)
dp.callback_query.register(set_location, TrainingSurvey.location)

dp.message.register(show_exercise_categories, F.text == "Упражнения 📚")
dp.callback_query.register(handle_category_selection, F.data.startswith("category_"))
dp.callback_query.register(handle_exercise_selection, F.data.startswith("exercise_"))
dp.callback_query.register(handle_back_to_categories, F.data == "back_to_categories")

dp.message.register(handle_button_click)


# Запуск бота
async def main():
    await set_bot_commands(bot)
    await dp.start_polling(bot)


if __name__ == "__main__":
    print("Bot is running...")
    asyncio.run(main())
