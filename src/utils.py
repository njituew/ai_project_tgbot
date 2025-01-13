import os
from dotenv import load_dotenv
import pandas as pd


'''
Функция для получения токена бота из .env файла
'''
def get_token() -> str:
    load_dotenv()
    token = os.getenv("BOT_TOKEN")

    # Проверка токена
    if not token:
        raise ValueError("BOT_TOKEN отсутствует в файле .env")
    return token


'''
Функция для создания (если его нет) книги по пути file_path
'''
def create_table(file_path: str) -> None:
    if not os.path.exists(file_path):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        df = pd.DataFrame(columns=["ID", "Name", "Age", "Height", "Weight", "BMI"])
        df.to_excel(file_path, index=False, engine="openpyxl")


'''
Функция для расчета ИМТ
'''
def calculate_bmi(height: int, weight: int) -> float:
    bmi = weight / (height / 100) ** 2
    return round(bmi, 1)    # чтобы была 1 цифра после запятой