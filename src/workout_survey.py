from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from apscheduler.schedulers.asyncio import AsyncIOScheduler


scheduler = AsyncIOScheduler()
users_with_answers = set()
users_without_training = set()


async def open_workout_survey(message: types.Message):
    user_id = message.from_user.id

    if user_id in users_with_answers:
        await message.answer("Сегодня вы уже прошли опрос")
    else:
        if user_id in users_without_training:
            await message.answer("Сегодня у вас нет тренировки 🥱")
        else:
            await message.answer(
                "Расскажите, как прошла ваша тренировка.\nВы выполнили все упражнения?\n\n",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="Нет, не все", callback_data="some_exercises_are_completed"),
                     InlineKeyboardButton(text="Да, все", callback_data="all_exercises_are_completed")],
                    [InlineKeyboardButton(text="Сегодня без тренировки", callback_data="not_today")],
                    [InlineKeyboardButton(text="Пройти опрос позже", callback_data="proceed_to_survey_later")]
                ])
            )


async def some_exercises(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id

    await callback_query.message.edit_text("+ 5 баллов")
    users_with_answers.add(user_id)


async def all_exercises(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id

    await callback_query.message.edit_text("+ 10 баллов")
    users_with_answers.add(user_id)


async def without_exercises(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id

    await callback_query.message.edit_text("- 5 баллов")
    users_with_answers.add(user_id)


async def defer_survey(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text("Опрос отложен 🕐")