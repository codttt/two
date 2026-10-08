import unittest

from src.main import (
    format_number,
    parse_row,
    swap_diagonals_by_columns,
    swap_diagonals_by_rows,
)


class DiagonalSwapTests(unittest.TestCase):
    def setUp(self):
        self.matrix = [
            [1.0, 2.0, 3.0, 4.0],
            [5.0, 6.0, 7.0, 8.0],
            [9.0, 10.0, 11.0, 12.0],
            [13.0, 14.0, 15.0, 16.0],
        ]

    def test_swap_by_rows_even_matrix(self):
        expected = [
            [4.0, 2.0, 3.0, 1.0],
            [5.0, 7.0, 6.0, 8.0],
            [9.0, 11.0, 10.0, 12.0],
            [16.0, 14.0, 15.0, 13.0],
        ]
        self.assertEqual(swap_diagonals_by_rows(self.matrix), expected)

    def test_swap_by_columns_even_matrix(self):
        expected = [
            [13.0, 2.0, 3.0, 16.0],
            [5.0, 10.0, 11.0, 8.0],
            [9.0, 6.0, 7.0, 12.0],
            [1.0, 14.0, 15.0, 4.0],
        ]
        self.assertEqual(swap_diagonals_by_columns(self.matrix), expected)

    def test_central_element_is_preserved_for_odd_size(self):
        matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        self.assertEqual(swap_diagonals_by_rows(matrix)[1][1], 5)
        self.assertEqual(swap_diagonals_by_columns(matrix)[1][1], 5)

    def test_single_element_matrix(self):
        self.assertEqual(swap_diagonals_by_rows([[5]]), [[5]])
        self.assertEqual(swap_diagonals_by_columns([[5]]), [[5]])

    def test_source_matrix_is_not_modified(self):
        source = [row[:] for row in self.matrix]
        swap_diagonals_by_rows(self.matrix)
        swap_diagonals_by_columns(self.matrix)
        self.assertEqual(self.matrix, source)

    def test_non_square_matrix_is_rejected(self):
        with self.assertRaises(ValueError):
            swap_diagonals_by_rows([[1, 2, 3], [4, 5, 6]])

    def test_empty_matrix_is_rejected(self):
        with self.assertRaises(ValueError):
            swap_diagonals_by_columns([])

    def test_parse_row_accepts_comma_separator(self):
        self.assertEqual(parse_row("1,5 -2 3.25", 3), [1.5, -2.0, 3.25])

    def test_parse_row_checks_length(self):
        with self.assertRaises(ValueError):
            parse_row("1 2", 3)

    def test_number_formatting(self):
        self.assertEqual(format_number(4.0), "4")
        self.assertEqual(format_number(4.25), "4.25")


if __name__ == "__main__":
    unittest.main()
