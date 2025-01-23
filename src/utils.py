import os
from dotenv import load_dotenv
import pandas as pd
import json
import random
import asyncio
from aiogram import types


'''
Функция для получения токена бота из .env файла
'''
def get_bot_token() -> str:
    load_dotenv()
    token = os.getenv("BOT_TOKEN")

    # Проверка токена
    if not token:
        raise ValueError("BOT_TOKEN отсутствует в файле .env")
    return token


'''
Функция для создания (если её нет) таблицы
'''
def create_table(file_path: str, colums: list[str]) -> None:
    if not os.path.exists(file_path):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        df = pd.DataFrame(columns=colums)
        df.to_excel(file_path, index=False)


'''
Функция для удаления пользователя из таблицы
'''
def remove_user(file_path: str, user_id: str) -> None:
    # Чтение таблицы из Excel
    df = pd.read_excel(file_path)

    # Приводим колонку 'ID' и значение user_id к единому типу и удаляем лишние пробелы
    df["ID"] = df["ID"].astype(str).str.strip()
    user_id = str(user_id).strip()

    # Фильтруем таблицу, оставляя только строки, где user_id не равен заданному
    df_filtered = df[df["ID"] != user_id]

    # Сохраняем обновлённую таблицу
    df_filtered.to_excel(file_path, index=False)



'''
Функция для расчета ИМТ
'''
def calculate_bmi(height: int, weight: int) -> float:
    bmi = weight / (height / 100) ** 2
    return round(bmi, 1)    # чтобы была 1 цифра после запятой


'''
Функция для преобразования ответа ИИ в json
'''
def str_to_json(raw_string: str):
    # Находим начало и конец JSON блока
    start_index = raw_string.find("{")
    end_index = raw_string.rfind("}") + 1
    if start_index == -1 or end_index == -1:
        raise ValueError("JSON не найден в строке")
    
    # Извлекаем JSON блок
    json_block = raw_string[start_index:end_index]

    # Удаляем лишние пробелы, многострочные кавычки и экранируем символы перевода строки
    json_block = json_block.replace('"""', '"').replace("    ", "")

    # Удаляем лишние пробелы между запятыми
    json_block = json_block.replace(", ", ",")

    parsed_json = json.loads(json_block)
    return parsed_json


'''
Функция для форматирования информации об упражнении
'''
def format_exercise_info(key, exercise_data):
    data = exercise_data.get(key)
    if not data:
        return "Информация об упражнении не найдена."

    # Разделяем описание, ошибки и ссылку
    
    description_errors, link = data.split(" Ссылка на видео: ")
    description, errors = description_errors.split(" Ключевые ошибки: ")
    errors_list = errors.split("; ")
    link_text = f"\nВидео с техникой упражнения: {link.strip()}"

    # Формируем текст
    formatted_text = "\n".join([
        description.strip(),
        "\nКлючевые ошибки:",
        *[f"- {error.strip()}" for error in errors_list],
        link_text
    ]).strip()

    return formatted_text


SPORT_QUOTES = [
    "В жизни всегда есть две дороги: одна — первая, а другая — вторая. 🚶‍♂️",
    "Мы должны оставаться мыми, а они – оними. 🏋️‍♂️",
    "Работа — это не волк. Работа — ворк. А волк — это ходить. 🐺",
    "Марианскую впадину знаешь? Это я упал. 🏊‍♂️",
    "Как говорил мой дед, «Я твой дед».",
    "Слово — не воробей. Вообще ничто не воробей, кроме самого воробья. 🐦",
    "Все будет хорошо, если не будет хуже. 🤞",
    "Работа не волк. Никто не волк. Только волк волк. 🐺",
    "Если закрыть глаза, становится темно. 🌚",
    "Тут — это вам не там. 🤷‍♂️",
    "Чистые пруды знаешь? Я почистил. 🏞️",
    "Слово пацана знаешь? Я сказал. 🤙",
    "Нужно делать как нужно, как не нужно — не нужно. 🤔",
]


'''
Функция для цитат
'''
async def update_message_with_quotes(sent_message: types.Message, stop_event: asyncio.Event, header: str):
    while not stop_event.is_set():
        quote = random.choice(SPORT_QUOTES)

        try:
            await sent_message.edit_text(f"{header} ⚙️\n\n{quote}")
        except Exception:
            pass

        await asyncio.sleep(4)
