from aiogram import types
from src.registration import EXCEL_FILE
from src.utils import calculate_bmi, create_table, remove_user
from src.survey_for_training import check_training, EXCEL_FILE_TRAINING, EXCEL_FILE_DIET
from src.reminders import remove_notifications
from src.my_statistics import EXCEL_FILE_STATISTICS
import pandas as pd
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext


def get_info(user_id: str) -> dict:
    df = pd.read_excel(EXCEL_FILE)
    df["ID"] = df["ID"].astype(str).str.strip()
    user_id = str(user_id).strip()

    user_data = df[df["ID"] == user_id]

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
        [InlineKeyboardButton(text="Обновить профиль 🔁", callback_data="update_profile")],
        [InlineKeyboardButton(text="Удалить свой профиль 🗑️", callback_data="remove_profile")],
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
    waiting_for_update_value = State()
    waiting_for_bot_score = State()


def update_user_info(user_id: str, field: str, value):
    df = pd.read_excel(EXCEL_FILE)
    df["ID"] = df["ID"].astype(str).str.strip()
    user_id = str(user_id).strip()

    user_index = df[df["ID"] == user_id].index
    if user_index.empty:
        raise ValueError("Пользователь не найден.")

    df.loc[user_index, field] = value

    if field in ["Weight", "Height"]:
        weight = float(df.loc[user_index, "Weight"].values[0])
        height = float(df.loc[user_index, "Height"].values[0])
        bmi = calculate_bmi(height, weight)
        df.loc[user_index, "BMI"] = bmi

    df.to_excel(EXCEL_FILE, index=False)


async def start_update_profile(message: types.Message):
    keyboard = create_update_keyboard()
    await message.answer("Что вы хотите изменить?", reply_markup=keyboard)


async def handle_update_profile(callback_query: types.CallbackQuery):
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
    await callback_query.message.edit_text("Действие отменено ❌")
    await state.clear()


REMOVED_USERS_EXCEL = "data/removed_users.xlsx"
colums = ["ID", "Reason", "Score"]
create_table(REMOVED_USERS_EXCEL, colums)


async def remove_profile_reson(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.edit_text("Пожалуйста, укажите причину, почему вы решили перестать пользоваться нашим ботом?",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Не вижу смысла", callback_data="remove_profile_ans_no_reson"), InlineKeyboardButton(text="Пользуюсь услугами тренера", callback_data="remove_profile_ans_new_trainer")],
        [InlineKeyboardButton(text="Пользуюсь альтернативным ботом", callback_data="remove_profile_ans_another_bot")],
        [InlineKeyboardButton(text="Другое", callback_data="remove_profile_ans_other")],
        [InlineKeyboardButton(text="Отмена ❌", callback_data="cancel_update")]]
    ))


async def remove_profile_score(callback_query: types.CallbackQuery, state: FSMContext):
    reason_mapping = {
        "remove_profile_ans_no_reson": "Не вижу смысла дальше пользоваться",
        "remove_profile_ans_new_trainer": "Пользуюсь услугами тренера",
        "remove_profile_ans_another_bot": "Пользуюсь альтернативным ботом",
        "remove_profile_ans_other": "Другое"
    }
    await state.update_data(reson=reason_mapping.get(callback_query.data))
    await callback_query.message.edit_text("Пожалуйста, перед уходом оцените нашего бота от 1 до 10:", reply_markup=create_cancel_button_keyboard())
    await state.set_state(UpdateProfile.waiting_for_bot_score)


async def remove_profile(message: types.Message, state: FSMContext):
    if not message.text.isdigit() or not (1 <= int(message.text) <= 10):
        await message.answer("Пожалуйста, укажите оценку числом от 1 до 10.")
        return
    await state.update_data(score=message.text)

    user_id = message.from_user.id

    if check_training(user_id):
        remove_user(EXCEL_FILE_TRAINING, user_id)
        remove_user(EXCEL_FILE_DIET, user_id)
        remove_notifications(user_id)
    remove_user(EXCEL_FILE, user_id)
    remove_user(EXCEL_FILE_STATISTICS, user_id)

    user_data = await state.get_data()
    df = pd.read_excel(REMOVED_USERS_EXCEL)
    user_frame = pd.DataFrame([{
        "ID": user_id,
        "Reason": user_data["reson"],
        "Score": user_data["score"]
    }])
    df = pd.concat([df, user_frame], ignore_index=True)
    df.to_excel(REMOVED_USERS_EXCEL, index=False)

    await message.answer("Ваш профиль успешно удалён. 🗑️\nЖдём вашего возвращения 💝")

    await state.clear()  # Завершаем FSM