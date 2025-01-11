from os import getenv
from dotenv import load_dotenv

def get_token():
    load_dotenv()
    token = getenv("BOT_TOKEN")

    # Проверка токена
    if not token:
        raise ValueError("BOT_TOKEN отсутствует в файле .env")
    return token