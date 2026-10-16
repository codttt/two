"""Ввод данных и формирование интеграционного запроса."""

from uuid import uuid4

from src.matrix_operations import validate_square_matrix


SCHEMA_VERSION = "1.0"


def read_size(input_func=input, output_func=print):
    """Считать положительный размер квадратной матрицы."""
    while True:
        try:
            size = int(input_func("Введите размер квадратной матрицы n: "))
            if size <= 0:
                raise ValueError
            return size
        except ValueError:
            output_func("Ошибка: n должно быть положительным целым числом.")


def parse_row(text, size):
    """Преобразовать строку в список из size вещественных чисел."""
    values = [float(item.replace(",", ".")) for item in text.split()]
    if len(values) != size:
        raise ValueError(f"требуется ровно {size} элементов")
    return values


def read_matrix(size, input_func=input, output_func=print):
    """Считать квадратную матрицу построчно с повтором ошибочного ввода."""
    matrix = []
    for row_number in range(1, size + 1):
        while True:
            raw = input_func(f"Строка {row_number}: ")
            try:
                row = parse_row(raw, size)
            except ValueError as error:
                output_func(f"Ошибка: {error}.")
                continue
            matrix.append(row)
            break
    return matrix


def build_request(matrix, method="both", request_id=None):
    """Создать сообщение для передачи в модуль обработки."""
    validate_square_matrix(matrix)
    if method not in {"rows", "columns", "both"}:
        raise ValueError("метод должен быть rows, columns или both")
    return {
        "schema_version": SCHEMA_VERSION,
        "request_id": request_id or uuid4().hex,
        "operation": "swap_diagonals",
        "method": method,
        "matrix": [row[:] for row in matrix],
    }
