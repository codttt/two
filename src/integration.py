"""Интеграция модулей обработки матрицы через JSON-сообщения."""

from src.errors import IntegrationError, InvalidMessageError, VersionConflictError
from src.input_module import SCHEMA_VERSION
from src.json_transport import read_json_message, write_json_message
from src.matrix_operations import (
    swap_diagonals_by_columns,
    swap_diagonals_by_rows,
    validate_square_matrix,
)


SUPPORTED_METHODS = {"rows", "columns", "both"}


def validate_request(message):
    """Проверить и нормализовать входное интеграционное сообщение."""
    if not isinstance(message, dict):
        raise InvalidMessageError("запрос должен быть объектом JSON")
    if message.get("schema_version") != SCHEMA_VERSION:
        raise VersionConflictError(
            f"поддерживается версия {SCHEMA_VERSION}, "
            f"получена {message.get('schema_version')!r}"
        )
    if message.get("operation") != "swap_diagonals":
        raise InvalidMessageError("неподдерживаемая операция")

    method = message.get("method")
    if method not in SUPPORTED_METHODS:
        raise InvalidMessageError("метод должен быть rows, columns или both")

    request_id = message.get("request_id")
    if not isinstance(request_id, str) or not request_id.strip():
        raise InvalidMessageError("request_id должен быть непустой строкой")

    matrix = message.get("matrix")
    try:
        validate_square_matrix(matrix)
    except ValueError as error:
        raise InvalidMessageError(str(error)) from error

    return {
        "schema_version": SCHEMA_VERSION,
        "request_id": request_id,
        "operation": "swap_diagonals",
        "method": method,
        "matrix": [row[:] for row in matrix],
    }


def integrate_request(message):
    """Выполнить обработку корректного запроса и сформировать ответ."""
    request = validate_request(message)
    matrix = request["matrix"]
    results = {}
    if request["method"] in {"rows", "both"}:
        results["rows"] = swap_diagonals_by_rows(matrix)
    if request["method"] in {"columns", "both"}:
        results["columns"] = swap_diagonals_by_columns(matrix)

    return {
        "schema_version": SCHEMA_VERSION,
        "request_id": request["request_id"],
        "status": "ok",
        "operation": request["operation"],
        "method": request["method"],
        "source_matrix": matrix,
        "results": results,
        "error": None,
    }


def error_response(message, error):
    """Создать унифицированный ответ об ошибке интеграции."""
    request_id = message.get("request_id") if isinstance(message, dict) else None
    return {
        "schema_version": SCHEMA_VERSION,
        "request_id": request_id,
        "status": "error",
        "operation": "swap_diagonals",
        "method": message.get("method") if isinstance(message, dict) else None,
        "source_matrix": None,
        "results": {},
        "error": {"code": getattr(error, "code", "invalid_data"), "message": str(error)},
    }


def process_request_file(request_path, response_path, timeout=0.0):
    """Прочитать запрос, интегрировать модули и записать ответ."""
    message = read_json_message(request_path, timeout=timeout)
    try:
        response = integrate_request(message)
    except (IntegrationError, ValueError) as error:
        response = error_response(message, error)
    write_json_message(response_path, response)
    return response
