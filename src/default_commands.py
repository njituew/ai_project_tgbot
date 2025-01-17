from aiogram import Bot, types
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, BotCommand

from src.registration import check_registered, RegistrationStates
from src.ai_generation import simple_message_to_ai
from src.my_profile import get_info
from src.survey_for_training import check_training, TrainingStates, set_wishes
from src.my_plan import get_plan


'''
Команда /start
'''
async def cmd_start(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user_name = check_registered(user_id)
    if user_name:
        await message.answer(f"С возвращением, {user_name}!\n\n/menu - открыть меню бота")
    else:
        await message.answer("Добро пожаловать! Давайте начнем регистрацию. Как вас зовут?")
        await state.set_state(RegistrationStates.waiting_for_name)


'''
Команда /menu
'''
async def cmd_menu(message: types.Message):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Создать тренировку 🏋️‍♂️"), KeyboardButton(text="Мой план 📋")],
            [KeyboardButton(text="Упражнения 📚"), KeyboardButton(text="Напоминания ⏰")],
            [KeyboardButton(text="Мой профиль 👤"), KeyboardButton(text="Моя статистика 📈")]
        ],
        resize_keyboard=True
    )
    await message.answer("Меню открыто", reply_markup=keyboard)


# Ручка для кнопок
async def handle_button_click(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    # Если пользователь находится в состоянии ожидания пожеланий, не обрабатываем это сообщение
    if current_state == TrainingStates.waiting_for_wishes:
        await set_wishes(message, state)
        return
    
    text = message.text
    if text in ("Моя статистика 📈"):
        await message.answer(text)
        return

    user_id = message.from_user.id
    user_info = get_info(user_id)
    user_training = get_plan(user_id) if check_training(user_id) else {}
    await message.answer(simple_message_to_ai(text, user_info, user_training))

async def set_bot_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Начать работу с ботом"),
        BotCommand(command="menu", description="Открыть главное меню"),
    ]
    await bot.set_my_commands(commands)
