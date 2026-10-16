"""Драйвер для автономной проверки нижнего модуля обработки."""

from src.matrix_operations import swap_diagonals_by_columns, swap_diagonals_by_rows


def main():
    matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    print("Проверка обмена по строкам:", swap_diagonals_by_rows(matrix))
    print("Проверка обмена по столбцам:", swap_diagonals_by_columns(matrix))


if __name__ == "__main__":
    main()
