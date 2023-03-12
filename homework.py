import logging
import sys
import time
from http import HTTPStatus

import requests
import telegram
from dotenv import dotenv_values

from exceptions import (EmptyResponseFromAPI, KeyErrorStatus)

config = dotenv_values(".env")

PRACTICUM_TOKEN = config.get("PRACTICUM_TOKEN")
TELEGRAM_TOKEN = config.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = config.get("TELEGRAM_CHAT_ID")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO)
handler = (
    logging.FileHandler("output.log"),
    logging.StreamHandler(sys.stdout))


logger = logging.getLogger(__name__)


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
    return all((PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID))


def send_message(bot, message):
    """Отправка сообщения в Telegram чат."""
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        logger.debug(f"Сообщение в Telegram чат {message} успешно отправлено")
    except telegram.TelegramError:
        logger.error("Ошибка отправки в Telegram чат")


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
    """Проверка ответа API."""
    logger.info("Начало проверки")
    try:
        homeworks = response["homeworks"]
    except KeyError:
        raise KeyError("Отсутствует ключ homeworks")
    if not isinstance(response, dict):
        raise EmptyResponseFromAPI("Несоответствие типа ответа API")
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
        raise KeyErrorStatus("Отсутствует статус домашней работы ")
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
        sys.exit("Отсутствуют переменные окружения")

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
