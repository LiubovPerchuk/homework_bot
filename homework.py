import logging
import os
import time
from http import HTTPStatus

import requests
import telegram
from dotenv import load_dotenv


load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO)

logger = logging.getLogger(__name__)

PRACTICUM_TOKEN = os.getenv("PRACTICUM_TOKEN")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

RETRY_PERIOD = 600
ENDPOINT = "https://practicum.yandex.ru/api/user_api/homework_statuses/"
HEADERS = {"Authorization": f"OAuth {PRACTICUM_TOKEN}"}


HOMEWORK_VERDICTS = {
    "approved": "Работа проверена: ревьюеру всё понравилось. Ура!",
    "reviewing": "Работа взята на проверку ревьюером.",
    "rejected": "Работа проверена: у ревьюера есть замечания."
}


def check_tokens():
    """Провека переменных окружения."""
    if PRACTICUM_TOKEN and TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        return True
    else:
        return False


def send_message(bot, message):
    """Отправка сообщения в Telegram чат."""
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        logger.debug(f"Сообщение в Telegram чат {message} успешно отправлено")
    except telegram.error.TelegramError as error:
        logger.error(f"Сообщение {message} не отправлено: {error}")


def get_api_answer(timestamp):
    """Проверка доступности API Яндекс.Практикума."""
    timestamp = int(time.time())
    params = {"from_date": timestamp}
    try:
        response = requests.get(
            ENDPOINT, headers=HEADERS, params=params)
        logger.info("Попытка соединения с сервером")
    except Exception as error:
        raise Exception(f"Ошибка соединения с сервером: {error}")
    if response.status_code == HTTPStatus.OK:
        return response.json()
    raise ConnectionError("Ошибка соединения с сервером")


def check_response(response):
    """Проверка наличия и статуса домашней работы."""
    logger.info("Начало проверки")
    try:
        homeworks = response["homeworks"]
    except KeyError:
        raise KeyError("Отсутствует ключ homeworks")
    if not isinstance(response, dict):
        raise TypeError("Несоответствие типа ответа API")
    if not isinstance(homeworks, list):
        raise TypeError("Ответ API должен быть списком!")
    return homeworks


def parse_status(homework):
    """Проверка изменения статуса домашней работы."""
    logger.info("Проверка статуса домашней работы начата.")
    if "homework_name" in homework:
        homework_name = homework.get("homework_name")
    else:
        raise KeyError("Домашней работы не существует")
    if "status" in homework:
        homework_status = homework.get("status")
    else:
        raise KeyError("Отсутствует статус")
    try:
        verdict = HOMEWORK_VERDICTS[homework_status]
    except KeyError:
        raise ValueError("Неизвестный запрос")
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    logger.info("Бот запущен")
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())
    if not check_tokens():
        logger.critical("Отсутствуют переменные окружения")
        raise ValueError("Несоответствующее значение токенов")

    while True:
        try:
            response = get_api_answer(timestamp)
            homework = check_response(response)
            if homework:
                send_message(bot, parse_status(homework[0]))
            else:
                logger.info("Статус не изменился")
        except Exception as error:
            logger.error(f"Сбой в работе программы: {error}")
        else:
            time.sleep(RETRY_PERIOD)


if __name__ == "__main__":
    main()
