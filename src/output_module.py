"""Форматирование и вывод результатов интеграции."""

from src.errors import InvalidMessageError


def format_number(value):
    """Представить число без лишних нулей после запятой."""
    return f"{value:g}"


def format_matrix(matrix):
    """Преобразовать матрицу в многострочный текст."""
    return "\n".join(" ".join(format_number(value) for value in row) for row in matrix)


def print_matrix(matrix, output_func=print):
    """Вывести матрицу построчно."""
    for line in format_matrix(matrix).splitlines():
        output_func(line)


def print_response(response, output_func=print):
    """Вывести успешный результат или сообщение об ошибке."""
    if response.get("status") == "error":
        error = response.get("error") or {}
        output_func(f"Ошибка интеграции [{error.get('code')}]: {error.get('message')}")
        return
    if response.get("status") != "ok":
        raise InvalidMessageError("ответ не содержит корректный статус")

    output_func("Исходная матрица:")
    print_matrix(response["source_matrix"], output_func)
    if "rows" in response["results"]:
        output_func("")
        output_func("Обмен диагоналей по строкам:")
        print_matrix(response["results"]["rows"], output_func)
    if "columns" in response["results"]:
        output_func("")
        output_func("Обмен диагоналей по столбцам:")
        print_matrix(response["results"]["columns"], output_func)
