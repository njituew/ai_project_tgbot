from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram import types


class TrainingSurvey(StatesGroup):
    goal = State()  # Состояние для цели тренировок
    level = State()  # Состояние для уровня сложности
    location = State()  # Состояние для места тренировок


def create_goal_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Набор массы 💪", callback_data="goal_mass")],
        [InlineKeyboardButton(text="Похудение 🏃", callback_data="goal_loss")],
        [InlineKeyboardButton(text="Поддержание формы 🤸", callback_data="goal_maintenance")]
    ])


def create_level_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Новичок 🥉", callback_data="level_beginner")],
        [InlineKeyboardButton(text="Средний 🥈", callback_data="level_intermediate")],
        [InlineKeyboardButton(text="Профессионал 🥇", callback_data="level_pro")]
    ])


def create_location_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Дом 🏠", callback_data="location_home")],
        [InlineKeyboardButton(text="Тренажерный зал 🏋️", callback_data="location_gym")]
    ])


async def start_survey(message: types.Message, state: FSMContext):
    await message.answer("Какова цель тренировок?", reply_markup=create_goal_keyboard())
    await state.set_state(TrainingSurvey.goal)


async def set_goal(callback_query: types.CallbackQuery, state: FSMContext):
    goal_mapping = {
        "goal_mass": "Набор массы",
        "goal_loss": "Похудение",
        "goal_maintenance": "Поддержание формы"
    }
    # Сохраняем выбор
    selected_goal = goal_mapping[callback_query.data]
    await state.update_data(goal=selected_goal)
    await callback_query.message.edit_text(
        "Каков ваш уровень?", reply_markup=create_level_keyboard()
    )
    await state.set_state(TrainingSurvey.level)


async def set_level(callback_query: types.CallbackQuery, state: FSMContext):
    level_mapping = {
        "level_beginner": "Новичок",
        "level_intermediate": "Средний",
        "level_pro": "Профессионал"
    }
    # Сохраняем выбор
    selected_level = level_mapping[callback_query.data]
    await state.update_data(level=selected_level)
    await callback_query.message.edit_text(
        "Где будут проходить тренировки?", reply_markup=create_location_keyboard()
    )
    await state.set_state(TrainingSurvey.location)


async def set_location(callback_query: types.CallbackQuery, state: FSMContext):
    location_mapping = {
        "location_home": "Дом",
        "location_gym": "Тренировочный зал"
    }
    # Сохраняем выбор
    selected_location = location_mapping[callback_query.data]
    await state.update_data(location=selected_location)

    # Собираем все данные
    data = await state.get_data()
    await callback_query.message.edit_text(
        f"Тренировка создана! Вот ваши параметры:\n"
        f"Цель: {data['goal']}\n"
        f"Уровень: {data['level']}\n"
        f"Место: {data['location']}"
    )
    await state.clear()  # Завершаем FSM