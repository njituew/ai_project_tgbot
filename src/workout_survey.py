from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from typing import Union
import pandas as pd
import datetime


EXCEL_FILE_TRAINING = "data/trainings.xlsx"

scheduler = AsyncIOScheduler()
users_with_answers = set()


# Проверка прошёл ли пользователь опрос
def check_user_in_answers_set(user_id: int):
    return user_id in users_with_answers


def check_training(user_id: str) -> bool:
    df = pd.read_excel(EXCEL_FILE_TRAINING)
    user = df[df["ID"] == user_id]
    return not user.empty


def training_for_today(user_id: int):
    # Чтение файла
    trainings_df = pd.read_excel(EXCEL_FILE_TRAINING)

    # Строки с нужным ID
    trainings_info = trainings_df[trainings_df["ID"] == user_id]

    # План на сегодня
    trainings_text = trainings_info.iloc[0].get(datetime.datetime.today().strftime("%A").lower())

    return trainings_text


# Создание опроса после тренировки
async def open_workout_survey(event: Union[types.Message, types.CallbackQuery]):
    user_id = event.from_user.id

    if check_training(user_id):
        if user_id in users_with_answers:
            await event.answer("Сегодня вы уже прошли опрос") # Пишется только при type == types.Message
        else:
            if not pd.notna(training_for_today(user_id)):
                await event.answer("Сегодня у вас нет тренировки 🥱") # Пишется только при type == types.Message
            else:
                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="Нет, не все", callback_data="some_exercises_are_completed"),
                    InlineKeyboardButton(text="Да, все", callback_data="all_exercises_are_completed")],
                    [InlineKeyboardButton(text="Сегодня без тренировки", callback_data="not_today")],
                    [InlineKeyboardButton(text="Пройти опрос позже", callback_data="proceed_to_survey_later")]
                ])
                if isinstance(event, types.CallbackQuery):
                    await event.message.edit_text(
                        "Расскажите, как прошла ваша тренировка.\nВы выполнили все упражнения?\n\n",
                        reply_markup=keyboard
                    )
                elif isinstance(event, types.Message):
                    await event.answer(
                        "Расскажите, как прошла ваша тренировка.\nВы выполнили все упражнения?\n\n",
                        reply_markup=keyboard
                    )
    else:  # Пишется только при type == types.Message
        await event.answer(
            "Вы не можете пройти опрос, так как на данный момент у вас нет плана тренировок.\n\n"
            "Создайте свой персональный план и добивайтесь успехов вместе с нашим ботом! 🏆",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Создать тренировку 🏋️‍♂️", callback_data="reminders_new_training")]
            ])
        )



# Функция для ответа "Нет, не все"
async def some_exercises(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id

    await callback_query.message.edit_text("Каждая тренировка — это шаг вперёд, даже если вы не сделали всё запланированное! ✨"
                                           "\nВ следующий раз попробуйте завершить все упражнения. "
                                           "Если есть сложности, напишите, чем я могу помочь.")
    users_with_answers.add(user_id)


# Функция для ответа "Да, все"
async def all_exercises(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id

    await callback_query.message.edit_text("Отлично, вы молодец! 🎉"
                                           "\nПродолжайте в том же духе. Помните: регулярность — ключ к успеху! 🚀")
    users_with_answers.add(user_id)


# Функция для ответа "Сегодня без тренировки"
async def without_exercises(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id

    await callback_query.message.edit_text("Ничего страшного, отдых — тоже важная часть тренировочного процесса! 🛌\n"
                                           "Не забывайте возвращаться к тренировкам, как только будете готовы 😊")
    users_with_answers.add(user_id)


# Функция для ответа "Пройти опрос позже"
async def defer_survey(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text("Опрос отложен 🕐")