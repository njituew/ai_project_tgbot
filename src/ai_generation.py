from langchain_mistralai import ChatMistralAI
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from dotenv import load_dotenv
from src.utils import str_to_json
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, MessagesState
from aiogram.types import Message


# Загрузка переменных из .env
load_dotenv()

# Инициализация ИИ
chat = ChatMistralAI(
    model="mistral-large-latest",
    # max_tokens=1000
)

prompt_template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """Ты – крутой фитнес-тренер мирового уровня с многолетним опытом работы. 
Ты отлично разбираешься в разработке индивидуальных тренировочных программ, правильном питании и мотивации. 
Твои клиенты ценят тебя за профессионализм, энтузиазм и персонализированный подход. 
Ты всегда поддерживаешь позитивное настроение, мотивируешь на достижение целей и 
подстраиваешь рекомендации под уникальные потребности и возможности каждого человека. 
При ответах старайся быть вдохновляющим, лаконичным и четким, но при этом предоставлять полезные и практические советы. 
Ты умеешь объяснять сложные вещи простым языком и создаешь ощущение, что каждый может достичь своих целей."""
        ),
        MessagesPlaceholder(variable_name="messages")
    ]
)

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
    "workout": ...
    "diet": ...
и так далее все дни недели (monday, tuesday, wednesday, thursday, friday, saturday, sunday).
Названия полей в JSON менять нельзя. В полях workout и diet должны быть str в которых между пунктами есть перенос строки.

Если в конкретный день тренировки нет, то для него "workout" оставляешь пустым,
но диета должна быть расписана для каждого дня.
Не может быть такого что за неделю не предусмотрена ни одна тренировка.
Составь для пользователя индивидуальный план, учитывая его результаты опроса:
{data},
и информация о нём:
{info}.
Постарайся учесть его пожелания ('wishes') в расписании тренировок и питания."""

SIMPLE_MESSAGE_TEMPLATE = """Информация о пользователе:
{info}
План тренировок и диета пользователя:
{training}

Ответь на сообщение пользователя:
{message}"""

SIMPLE_MESSAGE_TEMPLATE_WITHOUT_TRAINING = """Информация о пользователе:
{info}

Ответь на сообщение пользователя:
{message}
И предложи помочь создать план тренировок и диеты по команде /generate_plan (обязательно укажи эту команду),
но не предлагай конкретные упражнения или питание, если только
пользователь сам этого не попросит."""

MY_STATISTICS_TEMPLATE = """В статистике пользователя действуют следующие правила:
После выполнения каждой тренировки пользователь проходит опрос после тренировки.
В опросе задается вопрос о том, выполнил ли пользователь все упражнения тренировки, и есть три варианта ответа:
1. Да, все упражнения выполнены. (+ 10 баллов за данный вариант ответа)
2. Нет, не все упражнения выполнены. (+ 5 баллов за данный вариант ответа)
3. Нет, ни одно упражнение не выполнено. (-5 баллов за данный вариант ответа)
Количество пройденных опросов и суммарный балл за все опросы хранятся в базе данных для каждого пользователя.

Информация о пройденных опросах пользователя и суммарный балл за них:
{data}

В ответ на сообщение пользователя на основе данной информации составь отчет о статистике: проанализируй данные о пройденных опросах пользователя и суммарный балл за них,
и сделай вывод о его активности, прогрессе и достижениях.
Дай краткий комментарий о его результативности.
Начинай свой ответ с фразы "📈 Вот твоя статистика:(перевод строки)"
"""

async def call_model(state: MessagesState):
    prompt = prompt_template.invoke(state)
    response = await chat.ainvoke(prompt)
    return {"messages": response}


workflow = StateGraph(state_schema=MessagesState)
workflow.add_edge(START, "model")
workflow.add_node("model", call_model)

app = workflow.compile(checkpointer=MemorySaver())


async def generate_schedule(data: dict, info: dict, user_id: int) -> None:
    formatted_prompt = SCHEDULE_TEMPLATE.format(data=data, info=info)

    messages = [
        HumanMessage(content=formatted_prompt),
    ]
    
    config = {"configurable": {"thread_id": user_id}}

    response = (await app.ainvoke({"messages": messages, "response_format": {"type": "json_object"}}, config))["messages"][-1]

    try:
        result_json = str_to_json(response.content)
    except:
        print(f"String to JSON conversation error.\nInput:\n{data=}\n{info=}\n\nOutput:\n{response.content}", flush=True)
        result_json = generate_schedule(data, info, user_id)

    return result_json


async def simple_message_to_ai(message: Message, info: dict, training: dict) -> str:
    if len(training) == 0:
        formatted_prompt = SIMPLE_MESSAGE_TEMPLATE_WITHOUT_TRAINING.format(info=info, message=message.text)
    else:
        formatted_prompt = SIMPLE_MESSAGE_TEMPLATE.format(info=info, training=training, message=message.text)

    messages = [
        HumanMessage(content=formatted_prompt),
    ]

    user_id = message.from_user.id
    config = {"configurable": {"thread_id": user_id}}

    return (await app.ainvoke({"messages": messages}, config))["messages"][-1].content


async def generate_statistics_request(data: dict, user_id: int) -> str:
    formatted_prompt = MY_STATISTICS_TEMPLATE.format(data=data)

    messages = [
        HumanMessage(content=formatted_prompt),
    ]

    config = {"configurable": {"thread_id": user_id}}

    return (await app.ainvoke({"messages": messages}, config))["messages"][-1].content
