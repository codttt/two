"""Обмен элементов главной и побочной диагоналей квадратной матрицы."""


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


def validate_square_matrix(matrix):
    """Проверить, что матрица непустая и квадратная."""
    if not matrix or any(len(row) != len(matrix) for row in matrix):
        raise ValueError("матрица должна быть непустой и квадратной")


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


def format_number(value):
    """Представить число без лишних нулей после запятой."""
    return f"{value:g}"


def print_matrix(matrix, output_func=print):
    """Вывести матрицу построчно."""
    for row in matrix:
        output_func(" ".join(format_number(value) for value in row))


def main():
    size = read_size()
    print(f"Введите {size} строк по {size} вещественных чисел:")
    matrix = read_matrix(size)

    print("\nИсходная матрица:")
    print_matrix(matrix)

    print("\nОбмен диагоналей по строкам:")
    print_matrix(swap_diagonals_by_rows(matrix))

    print("\nОбмен диагоналей по столбцам:")
    print_matrix(swap_diagonals_by_columns(matrix))


if __name__ == "__main__":
    main()
