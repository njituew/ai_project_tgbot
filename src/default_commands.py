from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from src.registration import *
from src.utils import check_registered


'''
Команда /start
'''
async def cmd_start(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user_name = check_registered("data/users.xlsx", user_id)
    if user_name:
        await message.answer(f"С возвращением, {user_name}!")
    else:
        await message.answer("Добро пожаловать! Давайте начнем регистрацию. Как вас зовут?")
        await state.set_state(RegistrationStates.waiting_for_name)


'''
Команда /menu
'''
async def cmd_menu(message: types.Message):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Создать тренировку 🏋️‍♂️")],
            [KeyboardButton(text="Упражнения 📚")],
            [KeyboardButton(text="Моя статистика 📈")]
        ],
        resize_keyboard=True
    )
    await message.answer("Меню открыто.", reply_markup=keyboard)


# Ручка для кнопок (пока просто затычка)
async def handle_button_click(message: types.Message):
    text = message.text
    if text in ("Создать тренировку 🏋️‍♂️", "Упражнения 📚", "Моя статистика 📈"):
        await message.answer(f"{text}")
