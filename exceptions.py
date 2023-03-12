class NotToSendError(Exception):
    """Родительский класс для ошибок, которые не требуют отправки."""

    pass


class EmptyResponseFromAPI(NotToSendError):
    """Ошибка соединения с сервером."""

    pass


class KeyErrorStatus(NotToSendError):
    """Ошибка статуса домашней работы."""

    pass
