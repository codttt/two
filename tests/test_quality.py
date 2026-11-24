import json
import tempfile
import unittest
from pathlib import Path

from src.errors import (
    IntegrationError,
    IntegrationTimeoutError,
    InvalidMessageError,
    ModuleUnavailableError,
    VersionConflictError,
)
from src.input_module import build_request, parse_row
from src.integration import integrate_request, process_request_file
from src.json_transport import read_json_message, write_json_message
from src.main import main
from src.matrix_operations import validate_square_matrix
from src.output_module import format_matrix, format_number, print_matrix


class CombinatorialConditionTests(unittest.TestCase):
    """Проверки сочетаний условий варианта 14."""

    def test_valid_matrix_condition_combinations(self):
        matrices = (
            [[0]],
            [[-1.5]],
            [[1, 2], [3, 4]],
            [[1.0, -2], [0, 4.25]],
        )
        for matrix in matrices:
            with self.subTest(matrix=matrix):
                self.assertIsNone(validate_square_matrix(matrix))

    def test_invalid_matrix_condition_combinations(self):
        cases = {
            "not_list": None,
            "empty": [],
            "row_not_list": [(1,)],
            "not_square": [[1, 2], [3]],
            "boolean": [[True]],
            "text": [["1"]],
            "infinity": [[float("inf")]],
            "not_a_number": [[float("nan")]],
        }
        for name, matrix in cases.items():
            with self.subTest(name=name):
                with self.assertRaises(ValueError):
                    validate_square_matrix(matrix)

    def test_processing_method_combinations(self):
        matrix = [[1, 2], [3, 4]]
        expectations = {
            "rows": {"rows"},
            "columns": {"columns"},
            "both": {"rows", "columns"},
        }
        for method, expected_keys in expectations.items():
            with self.subTest(method=method):
                response = integrate_request(
                    build_request(matrix, method=method, request_id=method)
                )
                self.assertEqual(set(response["results"]), expected_keys)
                self.assertEqual(response["status"], "ok")

    def test_request_condition_combinations(self):
        valid = build_request([[1]], request_id="quality")
        changes = (
            ("schema_version", "2.0"),
            ("operation", "unknown"),
            ("method", "unknown"),
            ("request_id", ""),
            ("matrix", [[1, 2], [3]]),
        )
        for key, value in changes:
            with self.subTest(key=key):
                request = dict(valid)
                request[key] = value
                with self.assertRaises(IntegrationError):
                    integrate_request(request)


class ModuleUnitTests(unittest.TestCase):
    def test_error_codes_are_stable(self):
        self.assertEqual(IntegrationError.code, "integration_error")
        self.assertEqual(ModuleUnavailableError.code, "module_unavailable")
        self.assertEqual(IntegrationTimeoutError.code, "timeout")
        self.assertEqual(InvalidMessageError.code, "invalid_message")
        self.assertEqual(VersionConflictError.code, "version_conflict")

    def test_input_rows_and_decimal_separators(self):
        self.assertEqual(parse_row("1,5 -2 0", 3), [1.5, -2.0, 0.0])
        for text in ("", "1 2", "one"):
            with self.subTest(text=text):
                with self.assertRaises(ValueError):
                    parse_row(text, 3)

    def test_json_round_trip_and_unicode(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "nested" / "message.json"
            message = {"status": "готово", "values": [1, 2, 3]}
            write_json_message(path, message)
            self.assertEqual(read_json_message(path), message)
            self.assertEqual(json.loads(path.read_text(encoding="utf-8")), message)

    def test_output_helpers(self):
        self.assertEqual(format_number(2.0), "2")
        self.assertEqual(format_number(-2.25), "-2.25")
        self.assertEqual(format_matrix([[1, 2], [3.5, 4]]), "1 2\n3.5 4")
        lines = []
        print_matrix([[1, 2], [3, 4]], lines.append)
        self.assertEqual(lines, ["1 2", "3 4"])

    def test_command_line_requires_both_paths(self):
        with self.assertRaises(SystemExit):
            main(["--request", "request.json"])


class RegressionTests(unittest.TestCase):
    def test_nonfinite_text_is_rejected(self):
        for value in ("nan", "inf", "-inf"):
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError, "конечными"):
                    parse_row(value, 1)

    def test_malformed_request_creates_error_response(self):
        with tempfile.TemporaryDirectory() as directory:
            request_path = Path(directory) / "request.json"
            response_path = Path(directory) / "response.json"
            request_path.write_text("{broken", encoding="utf-8")

            response = process_request_file(request_path, response_path)

            self.assertEqual(response["status"], "error")
            self.assertEqual(response["error"]["code"], "invalid_message")
            self.assertEqual(read_json_message(response_path), response)


if __name__ == "__main__":
    unittest.main()
