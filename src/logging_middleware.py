import pandas as pd
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject
from datetime import datetime
from src.utils import create_table


EXCEL_LOG_FILE = "data/logs.xlsx"


class LoggingMiddleware(BaseMiddleware):
    def __init__(self):
        super().__init__()
        
        create_table(EXCEL_LOG_FILE, ["Время", "ID Пользователя", "Тип", "Содержание"])


    async def __call__(self, handler, event: TelegramObject, data: dict):
        log_data = {
            "Время": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "ID": None,
            "Тип": None,
            "Содержание": None,
        }

        # Обработка входящих событий
        if isinstance(event, Message):
            log_data["ID Пользователя"] = event.from_user.id
            log_data["Тип"] = "Сообщение"
            log_data["Содержание"] = event.text
        elif isinstance(event, CallbackQuery):
            log_data["ID Пользователя"] = event.from_user.id
            log_data["Тип"] = "Callback"
            log_data["Содержание"] = event.data

        # Логируем в Excel
        if log_data["ID Пользователя"]:
            self.log_to_excel(log_data)
        
        print(
            f'{log_data["Тип"]} by {event.from_user.username}: {log_data["Содержание"]}; ID: {log_data["ID Пользователя"]}, {log_data["Время"]}',
            flush=True
        )

        # Передаём обработку дальше
        response = await handler(event, data)

        # Логируем исходящее сообщение (если требуется)
        # Здесь можно дополнительно логировать ответы
        return response

    def log_to_excel(self, log_data):
        # Читаем существующий файл
        df = pd.read_excel(EXCEL_LOG_FILE)

        # Добавляем новую строку
        df = pd.concat([df, pd.DataFrame([log_data])], ignore_index=True)

        # Сохраняем файл обратно
        df.to_excel(EXCEL_LOG_FILE, index=False)
