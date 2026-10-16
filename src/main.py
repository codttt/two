"""Запуск интегрированной системы обработки матрицы."""

import argparse
from tempfile import TemporaryDirectory

from src.input_module import build_request, parse_row, read_matrix, read_size
from src.integration import process_request_file
from src.json_transport import write_json_message
from src.matrix_operations import (
    swap_diagonals_by_columns,
    swap_diagonals_by_rows,
    validate_square_matrix,
)
from src.output_module import format_number, print_matrix, print_response


__all__ = [
    "format_number",
    "parse_row",
    "print_matrix",
    "read_matrix",
    "read_size",
    "swap_diagonals_by_columns",
    "swap_diagonals_by_rows",
    "validate_square_matrix",
]


def run_interactive():
    """Выполнить полный цикл интеграции для консольного ввода."""
    size = read_size()
    print(f"Введите {size} строк по {size} вещественных чисел:")
    matrix = read_matrix(size)
    with TemporaryDirectory() as temporary_directory:
        request_path = f"{temporary_directory}/request.json"
        response_path = f"{temporary_directory}/response.json"
        write_json_message(request_path, build_request(matrix))
        response = process_request_file(request_path, response_path)
    print_response(response)


def main(arguments=None):
    """Запустить интерактивный режим или обработать JSON-файл."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--request", help="путь к входному JSON-файлу")
    parser.add_argument("--response", help="путь к выходному JSON-файлу")
    parser.add_argument("--timeout", type=float, default=0.0, help="таймаут ожидания")
    options = parser.parse_args(arguments)

    if options.request or options.response:
        if not options.request or not options.response:
            parser.error("--request и --response указываются вместе")
        response = process_request_file(options.request, options.response, options.timeout)
        print_response(response)
        return response
    run_interactive()


if __name__ == "__main__":
    main()
