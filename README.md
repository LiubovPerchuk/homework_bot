# Telegram-bot. Бот для проверки статуса домашней работы на код ревью в Яндекс.Практикум

Телеграм-бот для отслеживания статуса проверки домашней работы на Яндекс.Практикум.
Работает как на ПК так и на Heroku, достаточно запустить бота, прописать токены.
Каждые 10 минут бот проверяет API Яндекс.Практикум. И присылает в телеграм статус.
Если работа проверена вы получите сообщение о статусе вашего код ревью.
У API Практикум.Домашка есть лишь один эндпоинт:

https://practicum.yandex.ru/api/user_api/homework_statuses/

и доступ к нему возможен только по токену. Получить токен можно по [адресу] https://oauth.yandex.ru/authorize?response_type=token&client_id=1d0b9dd4d652455a9eb710d450ff456a. Копируем его, он нам пригодится чуть позже.

Принцип работы API
Когда ревьюер проверяет вашу домашнюю работу, он присваивает ей один из статусов:

- работа принята на проверку
- работа возвращена для исправления ошибок
- работа принята

## Технологии:
- Python 3.9
- python-dotenv 0.19.0
- python-telegram-bot 13.7

## Как запустить проект:

### Клонировать репозиторий и перейти в него в командной строке:

git clone git@github.com:LiubovPerchuk/homework_bot.git

cd homework_bot

### Cоздать и активировать виртуальное окружение:

python -m venv env

source env/bin/activate

### Установить зависимости из файла requirements.txt:

python -m pip install --upgrade pip

pip install -r requirements.txt

### Записать в переменные окружения (файл .env) необходимые ключи:

- токен профиля на Яндекс.Практикуме
- токен телеграм-бота
- свой ID в телеграме

### Запустить проект:

python homework.py
