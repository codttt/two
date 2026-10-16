"""Надежный обмен интеграционными сообщениями через JSON-файлы."""

import json
import os
import time
from pathlib import Path

from src.errors import (
    IntegrationTimeoutError,
    InvalidMessageError,
    ModuleUnavailableError,
)


POLL_INTERVAL = 0.02


def read_json_message(path, timeout=0.0):
    """Прочитать JSON, при необходимости ожидая появления файла."""
    source = Path(path)
    if timeout < 0:
        raise ValueError("таймаут не может быть отрицательным")

    deadline = time.monotonic() + timeout
    while not source.is_file():
        if timeout == 0:
            raise ModuleUnavailableError(f"файл обмена недоступен: {source}")
        if time.monotonic() >= deadline:
            raise IntegrationTimeoutError(f"истекло время ожидания файла: {source}")
        time.sleep(min(POLL_INTERVAL, max(0.0, deadline - time.monotonic())))

    try:
        raw = source.read_text(encoding="utf-8")
    except OSError as error:
        raise ModuleUnavailableError(f"не удалось прочитать файл: {source}") from error

    try:
        message = json.loads(raw)
    except json.JSONDecodeError as error:
        raise InvalidMessageError(f"некорректный JSON: {error.msg}") from error

    if not isinstance(message, dict):
        raise InvalidMessageError("корневой элемент JSON должен быть объектом")
    return message


def write_json_message(path, message):
    """Атомарно записать словарь в JSON-файл."""
    if not isinstance(message, dict):
        raise InvalidMessageError("для записи требуется объект JSON")

    destination = Path(path)
    temporary = destination.with_name(destination.name + ".tmp")
    try:
        destination.parent.mkdir(parents=True, exist_ok=True)
        temporary.write_text(
            json.dumps(message, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        os.replace(temporary, destination)
    except OSError as error:
        raise ModuleUnavailableError(f"не удалось записать файл: {destination}") from error
