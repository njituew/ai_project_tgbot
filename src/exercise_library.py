from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import json
from src.utils import format_exercise_info

JSON_FILE_PATH = "src/exercise_library_dict.json"

with open(JSON_FILE_PATH, "r", encoding="utf-8") as file:
    exercise_categories = json.load(file)


# Создание клавиатуры для категорий
def create_category_keyboard(exercise_categories):
    buttons = [
        [InlineKeyboardButton(text=category, callback_data=f"category_{category}")]
        for category in exercise_categories.keys()
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# Создание клавиатуры для упражнений в выбранной категории
def create_exercise_keyboard(category_key, exercise_categories):
    exercises = exercise_categories.get(category_key, {})
    if not exercises:
        raise ValueError(f"Категория '{category_key}' не найдена или пуста.")

    buttons = [
        [InlineKeyboardButton(text=description.split(":")[0], callback_data=key)]
        for key, description in exercises.items()
    ]
    # Кнопка "Назад" для возврата к категориям
    buttons.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_categories")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# Обработчик команды /menu
async def show_exercise_categories(message: types.Message):
    keyboard = create_category_keyboard(exercise_categories)
    await message.answer("Выберите категорию упражнений:", reply_markup=keyboard)


# Обработчик выбора категории
async def handle_category_selection(callback_query: types.CallbackQuery):
    category_key = callback_query.data.replace("category_", "")
    if category_key in exercise_categories:
        keyboard = create_exercise_keyboard(category_key, exercise_categories)
        await callback_query.message.edit_text(
            f"Упражнения в категории: {category_key}",
            reply_markup=keyboard
        )
    else:
        await callback_query.message.answer("Категория не найдена.")
    await callback_query.answer()


# Обработчик выбора упражнения
async def handle_exercise_selection(callback_query: types.CallbackQuery):
    for category, exercises in exercise_categories.items():
        if callback_query.data in exercises:
            exercise_info = format_exercise_info(callback_query.data, exercises)
            # Редактируем сообщение и сохраняем текущую клавиатуру
            await callback_query.message.edit_text(
                text=f"{exercise_info}\n\nВыберите другое упражнение, если хотите:",
                reply_markup=callback_query.message.reply_markup,  # Сохраняем текущую клавиатуру
            )
            await callback_query.answer()  # Убираем "часы"
            return

    await callback_query.answer("Упражнение не найдено.", show_alert=True)


# Обработчик кнопки "Назад"
async def handle_back_to_categories(callback_query: types.CallbackQuery):
    keyboard = create_category_keyboard(exercise_categories)
    await callback_query.message.edit_text("Выберите категорию упражнений:", reply_markup=keyboard)
    await callback_query.answer()
