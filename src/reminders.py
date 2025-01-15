from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot
from aiogram.fsm.context import FSMContext  # Импорт FSMContext для работы с состояниями
from apscheduler.triggers.cron import CronTrigger


scheduler = AsyncIOScheduler()

# Создание клавиатуры для выбора действия
def create_reminders_keyboard():
    buttons = [
        [InlineKeyboardButton(text="Включить✅", callback_data="turn_on_reminder")],
        [InlineKeyboardButton(text="Отключить❌", callback_data="turn_off_reminder")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# Отображение клавиатуры
async def show_reminders_menu(message: types.Message):
    keyboard = create_reminders_keyboard()
    await message.answer("Выберите действие для напоминаний:", reply_markup=keyboard)


# Функция для отправки сообщения пользователю
async def send_notification(bot: Bot, user_id: int):
    try:
        await bot.send_message(chat_id=user_id, text="Напоминание о тренировке")
    except Exception as e:
        print(f"Ошибка при отправке сообщения пользователю {user_id}: {e}")


# Функция для планирования уведомлений
async def schedule_notifications(callback_query: types.CallbackQuery, bot: Bot):
    user_id = callback_query.from_user.id

    hours = [8, 18]

    for hour in hours:
        # Создание задачи на основе времени
        scheduler.add_job(
            send_notification,
            CronTrigger(hour=hour, minute=0),
            args=[bot, user_id],  # Передаем bot и user_id в задачу
            id=f"notification_{user_id}_{hour}",  # Уникальный ID задачи
            replace_existing=True  # Заменить задачу, если ID совпадает
        )
    
    # Подтверждение обратного вызова
    await callback_query.message.edit_text("Напоминания включены!\nТеперь они будут приходить вам каждый день в 08:00 и 18:00.")


# Функция для отключения напоминаний
async def disabling_notifications(callback_query: types.CallbackQuery, bot: Bot):
    user_id = callback_query.from_user.id

    hours = [8, 18]

    for hour in hours:
        # Удаление задачи на основе времени
        scheduler.remove_job(f"notification_{user_id}_{hour}")
    
    # Подтверждение обратного вызова
    await callback_query.message.edit_text("Напоминания отключены!")

async def on_startup():
    scheduler.start()