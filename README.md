
# AI Sports Coach Telegram Bot

The telegram bot is available at @project_trainer_bot

---

# RU

AI Sports Coach Telegram Bot — это проект, предоставляющий возможность пользователям взаимодействовать с интеллектуальным тренером через Telegram. Бот помогает с составлением индивидуальных тренировочных планов, диет, а также отвечает на вопросы, связанные с фитнесом и здоровым образом жизни.

## Установка и запуск

Следуйте этим шагам, чтобы запустить проект локально:

### 1. Клонирование репозитория

Склонируйте репозиторий на ваш  компьютер:

```bash
git clone https://github.com/njituew/ai_project_tgbot.git

cd ai_project_tgbot
```

### 2. Создание виртуального окружения

Создайте виртуальное окружение для управления зависимостями:

```bash
python3 -m venv .venv
```

Активируйте виртуальное окружение:

- На Windows:
  ```bash
  .venv\Scripts\activate
  ```
- На macOS/Linux:
  ```bash
  source .venv/bin/activate
  ```

### 3. Установка зависимостей

Установите необходимые библиотеки:

```bash
pip install -r requirements.txt --no-deps
```

### 4. Настройка окружения

Создайте файл `.env` в корневой папке проекта и добавьте следующие строки:

```env
BOT_TOKEN=<ваш_токен_бота>
MISTRAL_API_KEY=<ваш_ключ_для_работы_с_API_MistralAI>
```

Ключ для работы с MistralAI можно создать [здесь](https://console.mistral.ai/api-keys/).

Замените `<ваш_токен_бота>` и `<ваш_ключ_для_работы_с_API>` соответствующими значениями.

### 5. Запуск бота

Запустите бота с помощью следующей команды:

```bash
python3 main.py
```

## Использование

После запуска бота вы можете взаимодействовать с ним в Telegram. Введите команду `/start`, чтобы начать, и следуйте инструкциям.

## Требования

- Python 3.8 или выше
- Установленный Telegram-бот с токеном, созданным через BotFather
- API-ключ для подключения к необходимым сервисам

## Вклад в проект

Вы можете создать pull request или открыть issue, чтобы предложить новые функции или сообщить об ошибках.

---

# EN

AI Sports Coach Telegram Bot is a project that enables users to interact with an intelligent coach via Telegram. The bot assists in creating personalized workout plans and diets, as well as answering questions related to fitness and a healthy lifestyle.

## Installation and Setup

Follow these steps to run the project locally:

### 1. Cloning the Repository

Clone the repository to your computer:

```bash
git clone https://github.com/njituew/ai_project_tgbot.git
cd ai_project_tgbot
```

### 2. Creating a Virtual Environment

Set up a virtual environment to manage dependencies:
```bash
python3 -m venv .venv
```
Activate the virtual environment:
- On Windows:
```bash
.venv\Scripts\activate
```
- On macOS/Linux:
```bash
source .venv/bin/activate
```

### 3. Installing Dependencies

Install the required libraries:

```bash
pip install -r requirements.txt --no-deps
```

### 4. Environment Configuration

Create a `.env` file in the root directory of the project and add the following lines:

```env
BOT_TOKEN=<your_bot_token>
MISTRAL_API_KEY=<your_mistral_api_key>
```
You can obtain the MistralAI API key [here](https://console.mistral.ai/api-keys/).
Replace `<your_bot_token>` and `<your_mistral_api_key>` with the appropriate values.

### 5. Running the Bot

Launch the bot using the following command:

```bash
python3 main.py
```

## Usage

Once the bot is running, you can interact with it in Telegram. Type the `/start` command to begin and follow the instructions provided.

## Requirements

- Python 3.8 or higher
- A Telegram bot with a token created via BotFather
- An API key for connecting to the required services

## Contributing

Feel free to submit a pull request or open an issue to suggest new features or report bugs.