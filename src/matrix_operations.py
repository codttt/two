"""Операции над квадратной матрицей."""

from math import isfinite


def validate_square_matrix(matrix):
    """Проверить, что матрица непустая, квадратная и содержит числа."""
    if not isinstance(matrix, list) or not matrix:
        raise ValueError("матрица должна быть непустым списком")

    size = len(matrix)
    for row in matrix:
        if not isinstance(row, list) or len(row) != size:
            raise ValueError("матрица должна быть квадратной")
        for value in row:
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ValueError("элементы матрицы должны быть числами")
            if not isfinite(value):
                raise ValueError("элементы матрицы должны быть конечными числами")


def swap_diagonals_by_rows(matrix):
    """Поменять диагональные элементы внутри каждой строки."""
    validate_square_matrix(matrix)
    result = [row[:] for row in matrix]
    size = len(result)
    for row_index in range(size):
        secondary_column = size - 1 - row_index
        result[row_index][row_index], result[row_index][secondary_column] = (
            result[row_index][secondary_column],
            result[row_index][row_index],
        )
    return result


def swap_diagonals_by_columns(matrix):
    """Поменять диагональные элементы внутри каждого столбца."""
    validate_square_matrix(matrix)
    result = [row[:] for row in matrix]
    size = len(result)
    for column_index in range(size):
        secondary_row = size - 1 - column_index
        result[column_index][column_index], result[secondary_row][column_index] = (
            result[secondary_row][column_index],
            result[column_index][column_index],
        )
    return result
