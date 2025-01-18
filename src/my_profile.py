from aiogram import types
from src.registration import EXCEL_FILE
from src.utils import calculate_bmi
import pandas as pd
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext


def get_info(user_id: str) -> dict:
    df = pd.read_excel(EXCEL_FILE)
    df["ID"] = df["ID"].astype(str).str.strip()
    user_id = str(user_id).strip()

    # Фильтруем строку по user_id
    user_data = df[df["ID"] == user_id]

    # Убираем колонку ID, преобразуем в словарь
    return user_data.drop(columns=["ID"]).iloc[0].to_dict()


def bmi_info(bmi: float) -> str:
    if bmi <= 16:
        bmi_info = "выраженный дефицит массы тела"
    elif bmi < 18.5:
        bmi_info = "недостаточная масса тела"
    elif bmi <= 25:
        bmi_info = "норма"
    elif bmi <= 30:
        bmi_info = "избыточная масса тела (предожирение)"
    elif bmi <= 35:
        bmi_info = "ожирение первой степени"
    elif bmi < 40:
        bmi_info = "ожирение второй степени"
    else:
        bmi_info = "ожирение третьей степени (морбидное)"
    return bmi_info


async def show_profile_info(message: types.Message):
    user_id = message.from_user.id
    
    user_info = get_info(user_id)
    
    bmi = float(user_info['BMI'])
    
    await message.answer(
        "Ваш профиль:\n\n"
        f"Имя: {user_info['Name']}\n"
        f"Пол: {user_info['Gender']}\n"
        f"Возраст: {user_info['Age']}\n"
        f"Рост: {user_info['Height']}\n"
        f"Вес: {user_info['Weight']}\n"
        f"Индекс массы тела: {user_info['BMI']} ({bmi_info(bmi)}*)\n\n"
        f"* - данные предоставлены таблицей ИМТ согласно ВОЗ и не являются диагнозом",
        reply_markup=create_update_button()
    )


def create_update_button():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Обновить профиль", callback_data="update_profile")],
    ])
    return keyboard


def create_select_gender_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Мужской ♂️", callback_data="gender_male")],
        [InlineKeyboardButton(text="Женский ♀️", callback_data="gender_female")],
        [InlineKeyboardButton(text="Отмена ❌", callback_data="cancel_update")],
    ])
    return keyboard


def create_cancel_button_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Отмена ❌", callback_data="cancel_update")],
    ])
    return keyboard


def create_update_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Имя", callback_data="update_name")],
        [InlineKeyboardButton(text="Пол", callback_data="update_gender")],
        [InlineKeyboardButton(text="Возраст", callback_data="update_age")],
        [InlineKeyboardButton(text="Рост", callback_data="update_height")],
        [InlineKeyboardButton(text="Вес", callback_data="update_weight")],
        [InlineKeyboardButton(text="Отмена ❌", callback_data="cancel_update")],
    ])
    return keyboard


class UpdateProfile(StatesGroup):
    waiting_for_value = State()


def update_user_info(user_id: str, field: str, value):
    df = pd.read_excel(EXCEL_FILE)
    df["ID"] = df["ID"].astype(str).str.strip()
    user_id = str(user_id).strip()

    # Находим индекс строки с данным user_id
    user_index = df[df["ID"] == user_id].index
    if user_index.empty:
        raise ValueError("Пользователь не найден.")

    # Обновляем значение
    df.loc[user_index, field] = value

    # Пересчет BMI, если обновляется вес или рост
    if field in ["Weight", "Height"]:
        weight = float(df.loc[user_index, "Weight"].values[0])
        height = float(df.loc[user_index, "Height"].values[0])
        bmi = calculate_bmi(height, weight)
        df.loc[user_index, "BMI"] = bmi

    # Сохраняем файл
    df.to_excel(EXCEL_FILE, index=False)


async def start_update_profile(message: types.Message):
    keyboard = create_update_keyboard()
    await message.answer("Что вы хотите изменить?", reply_markup=keyboard)


async def handle_update_profile(callback_query: types.CallbackQuery, state: FSMContext):
    await start_update_profile(callback_query.message)
    await callback_query.answer()


async def handle_field_selection(callback_query: types.CallbackQuery, state: FSMContext):
    field_map = {
        "update_name": "Name",
        "update_gender": "Gender",
        "update_age": "Age",
        "update_height": "Height",
        "update_weight": "Weight",
    }

    field_map1 = {
        "Name": "имени",
        "Age": "возраста",
        "Height": "роста",
        "Weight": "веса",
    }

    field = field_map.get(callback_query.data)
    field1 = field_map1.get(field)
    if field == "Gender":
        await state.update_data(field=field)
        await callback_query.message.edit_text("Выберите новое значение пола:", reply_markup=create_select_gender_keyboard())
    elif field:
        await state.update_data(field=field)
        await callback_query.message.edit_text(f"Введите новое значение {field1}:", reply_markup=create_cancel_button_keyboard())
        await state.set_state(UpdateProfile.waiting_for_value)

    await callback_query.answer()


async def process_value_update(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    data = await state.get_data()
    field = data["field"]
    value = message.text

    try:
        # Валидация значений
        if field == "Age":
            if not value.isdigit():
                await message.answer("Пожалуйста, укажите возраст числом:")
                return
            elif not (1 <= int(value) <= 150):
                await message.answer("Пожалуйста, укажите свой настоящий возраст:")
                return
        elif field == "Height":
            if not value.isdigit():
                await message.answer("Пожалуйста, укажите рост числом:")
                return
            elif not (100 <= int(value) <= 300):
                await message.answer("Пожалуйста, укажите свой настоящий рост:")
                return
        elif field == "Weight":
            if not value.isdigit():
                await message.answer("Пожалуйста, укажите вес числом:")
                return
            elif not (1 <= int(value) <= 600):
                await message.answer("Пожалуйста, укажите свой настоящий вес:")
                return
        
        field_map1 = {
            "Name": "Имя",
            "Age": "Возраст",
            "Height": "Рост",
            "Weight": "Вес",
        }
        field1 = field_map1.get(field)

        # Обновление информации
        update_user_info(user_id, field, value)

        if field in ["Height", "Weight"]:
            user_info = get_info(user_id)
            bmi = user_info["BMI"]
            await message.answer(
                f"{field1} успешно обновлен!\nВаш ИМТ пересчитан: {bmi} ({bmi_info(float(bmi))}*)\n"
                f"* - данные предоставлены таблицей ИМТ согласно ВОЗ и не являются диагнозом",
            )
        elif field == "Name":
            await message.answer(f"{field1} успешно обновлено!")
        else:
            await message.answer(f"{field1} успешно обновлен!")
    except ValueError as e:
        await message.answer(f"Ошибка: {str(e)}")
    except Exception as e:
        await message.answer("Произошла ошибка при обновлении данных.")

    await state.clear()


async def handle_gender_selection(callback_query: types.CallbackQuery, state: FSMContext):
    gender_map = {
        "gender_male": "Мужской",
        "gender_female": "Женский",
    }

    gender = gender_map.get(callback_query.data)
    if gender:
        user_id = callback_query.from_user.id
        data = await state.get_data()
        field = data["field"]

        try:
            update_user_info(user_id, field, gender)
            await callback_query.message.edit_text(f"Пол успешно обновлён!")
        except ValueError as e:
            await callback_query.message.edit_text(f"Ошибка: {str(e)}")
        except Exception as e:
            await callback_query.message.edit_text("Произошла ошибка при обновлении данных.")

        await state.clear()

    await callback_query.answer()


async def cancel_update(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.edit_text("Обновление отменено ❌")
    await state.clear()