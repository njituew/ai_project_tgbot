import pandas as pd
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject
from datetime import datetime

EXCEL_LOG_FILE = "data/logs.xlsx"

class LoggingMiddleware(BaseMiddleware):
    def __init__(self):
        super().__init__()

        # Создаём файл, если его нет
        try:
            pd.read_excel(EXCEL_LOG_FILE)
        except FileNotFoundError:
            df = pd.DataFrame(columns=["Время", "ID Пользователя", "Тип", "Содержание"])
            df.to_excel(EXCEL_LOG_FILE, index=False)

    async def __call__(self, handler, event: TelegramObject, data: dict):
        log_data = {
            "Время": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "ID Пользователя": None,
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
