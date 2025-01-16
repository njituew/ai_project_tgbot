from langchain_gigachat import GigaChat
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv
from src.utils import str_to_json


# Загрузка переменных из .env
load_dotenv()

# Инициализация GigaChat
chat = GigaChat(verify_ssl_certs=False, scope="GIGACHAT_API_PERS")

DEFAULT_SYSTEM_PROMPT = """Ты – крутой фитнес-тренер мирового уровня с многолетним опытом работы. 
Ты отлично разбираешься в разработке индивидуальных тренировочных программ, правильном питании и мотивации. 
Твои клиенты ценят тебя за профессионализм, энтузиазм и персонализированный подход. 
Ты всегда поддерживаешь позитивное настроение, мотивируешь на достижение целей и 
подстраиваешь рекомендации под уникальные потребности и возможности каждого человека. 
При ответах старайся быть вдохновляющим, лаконичным и четким, но при этом предоставлять полезные и практические советы. 
Ты умеешь объяснять сложные вещи простым языком и создаешь ощущение, что каждый может достичь своих целей."""

SCHEDULE_TEMPLATE = """Составь грамотный план тренировок и питания для пользователя на каждый день недели.
Верни его в виде json где для каждого дня недели подробно расписаны
план тренировки и питание.
В плане тренировок должны быть пронумерованные пункты с названиями упражнений,
а через двоеточие написаны количество подходов и время/количество повторений/т.п.
В питании должно быть описание всех необходимых приёмов пищи.

Json должен быть в формате:

"monday":
    "workout": "1. Упражнение 1: количество подходов и повторений/время выполнения упражнения\n2. Упражнение 2: ..."
    "diet": "Завтрак: блюдо на завтрак\n..."
"tuesday":
    "workout": ""
    "diet": ""

и так далее все дни недели.
В полях workout и diet должны быть str в которых между пунктами есть перенос строки.

Если в конкретный день тренировки нет, то для него "workout" оставляешь пустым,
но диета должна быть расписана для каждого дня.
Не может быть такого что за неделю не предусмотрена ни одна тренировка.
Составь для пользователя индивидуальный план, учитывая его результаты опроса:
{data},
и информация о нём:
{info}."""

SIMPLE_MESSAGE_TEMPLATE = """Информация о пользователе:
{info}
План тренировок и диета пользователя:
{training}

Ответь на сообщение пользователя:
{message}
Обращайся к пользователю по имени."""

SIMPLE_MESSAGE_TEMPLATE_WITHOUT_TRAINING = """Информация о пользователе:
{info}

Ответь на сообщение пользователя:
{message}
И предложи помочь создать план тренировок и диеты по команде /menu (обязательно укажи эту команду),
но не предлагай конкретные упражнения или питание, если только
пользователь сам этого не попросит. Обращайся к пользователю по имени."""


def generate_schedule(data: dict, info: dict) -> None:
    formatted_prompt = SCHEDULE_TEMPLATE.format(data=data, info=info)

    # Подготовка сообщений
    messages = [
        SystemMessage(content=DEFAULT_SYSTEM_PROMPT),
        HumanMessage(content=formatted_prompt)
    ]

    # Отправка запроса
    response = chat.invoke(messages)
    
    try:
        result_json = str_to_json(response.content)
    except:
        print(f"AI generation error.\nInput:\n{data=}\n{info=}\n\nOutput:\n{response.content}")
        result_json = generate_schedule(data, info)

    return result_json


def simple_message_to_ai(message: str, info: dict, training: dict) -> str:
    if len(training) == 0:
        formatted_prompt = SIMPLE_MESSAGE_TEMPLATE_WITHOUT_TRAINING.format(info=info, message=message)
    else:
        formatted_prompt = SIMPLE_MESSAGE_TEMPLATE.format(info=info, training=training, message=message)

    # Подготовка сообщений
    messages = [
        SystemMessage(content=DEFAULT_SYSTEM_PROMPT),
        HumanMessage(content=formatted_prompt)
    ]

    return chat.invoke(messages).content
