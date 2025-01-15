import os
from dotenv import load_dotenv
import pandas as pd
import json


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
    # Удаляем маркеры ```json и ```
    cleaned_string = raw_string.replace("```json", "").replace("```", "").strip()
    
    # Удаляем лишние пробелы и экранируем символы перевода строки
    cleaned_string = cleaned_string.replace("\n", "").replace("    ", "")
    
    # Преобразуем строку в JSON
    parsed_json = json.loads(cleaned_string)
    
    return parsed_json