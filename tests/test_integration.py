import json
import tempfile
import time
import unittest
from pathlib import Path
from threading import Thread
from unittest.mock import patch

from src.errors import (
    IntegrationTimeoutError,
    InvalidMessageError,
    ModuleUnavailableError,
    VersionConflictError,
)
from src.input_module import build_request, read_matrix, read_size
from src.integration import integrate_request, process_request_file, validate_request
from src.json_transport import read_json_message, write_json_message
from src.main import main, run_interactive
from src.matrix_operations import validate_square_matrix
from src.output_module import format_matrix, print_response


class IntegrationTests(unittest.TestCase):
    def setUp(self):
        self.matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]

    def test_build_request_contains_version_and_identifier(self):
        request = build_request(self.matrix, request_id="test-1")
        self.assertEqual(request["schema_version"], "1.0")
        self.assertEqual(request["request_id"], "test-1")
        self.assertEqual(request["method"], "both")

    def test_build_request_rejects_unknown_method(self):
        with self.assertRaises(ValueError):
            build_request(self.matrix, method="unknown")

    def test_read_size_repeats_invalid_value(self):
        answers = iter(["0", "three", "3"])
        messages = []
        size = read_size(lambda _prompt: next(answers), messages.append)
        self.assertEqual(size, 3)
        self.assertEqual(len(messages), 2)

    def test_read_matrix_repeats_invalid_row(self):
        answers = iter(["1", "1 2", "3 4"])
        messages = []
        matrix = read_matrix(2, lambda _prompt: next(answers), messages.append)
        self.assertEqual(matrix, [[1.0, 2.0], [3.0, 4.0]])
        self.assertEqual(len(messages), 1)

    def test_end_to_end_file_exchange(self):
        with tempfile.TemporaryDirectory() as directory:
            request_path = Path(directory) / "request.json"
            response_path = Path(directory) / "response.json"
            write_json_message(request_path, build_request(self.matrix, request_id="e2e"))
            response = process_request_file(request_path, response_path)
            saved_response = read_json_message(response_path)

        self.assertEqual(response, saved_response)
        self.assertEqual(response["status"], "ok")
        self.assertEqual(response["results"]["rows"], [[3, 2, 1], [4, 5, 6], [9, 8, 7]])
        self.assertEqual(
            response["results"]["columns"],
            [[7, 2, 9], [4, 5, 6], [1, 8, 3]],
        )

    def test_rows_only(self):
        response = integrate_request(build_request(self.matrix, method="rows"))
        self.assertIn("rows", response["results"])
        self.assertNotIn("columns", response["results"])

    def test_columns_only(self):
        response = integrate_request(build_request(self.matrix, method="columns"))
        self.assertIn("columns", response["results"])
        self.assertNotIn("rows", response["results"])

    def test_version_conflict_is_detected(self):
        request = build_request(self.matrix)
        request["schema_version"] = "2.0"
        with self.assertRaises(VersionConflictError):
            validate_request(request)

    def test_invalid_operation_is_detected(self):
        request = build_request(self.matrix)
        request["operation"] = "unknown"
        with self.assertRaises(InvalidMessageError):
            validate_request(request)

    def test_invalid_request_shape_and_identifier_are_detected(self):
        with self.assertRaises(InvalidMessageError):
            validate_request([])
        request = build_request(self.matrix)
        request["request_id"] = ""
        with self.assertRaises(InvalidMessageError):
            validate_request(request)

    def test_unknown_method_is_detected(self):
        request = build_request(self.matrix)
        request["method"] = "diagonal"
        with self.assertRaises(InvalidMessageError):
            validate_request(request)

    def test_invalid_matrix_produces_error_response(self):
        request = build_request(self.matrix, request_id="bad-matrix")
        request["matrix"] = [[1, 2], [3]]
        with tempfile.TemporaryDirectory() as directory:
            request_path = Path(directory) / "request.json"
            response_path = Path(directory) / "response.json"
            write_json_message(request_path, request)
            response = process_request_file(request_path, response_path)
        self.assertEqual(response["status"], "error")
        self.assertEqual(response["error"]["code"], "invalid_message")

    def test_missing_file_reports_unavailable_module(self):
        with self.assertRaises(ModuleUnavailableError):
            read_json_message("/definitely/missing/request.json")

    def test_negative_timeout_is_rejected(self):
        with self.assertRaises(ValueError):
            read_json_message("request.json", timeout=-1)

    def test_waiting_for_file_times_out(self):
        with tempfile.TemporaryDirectory() as directory:
            missing = Path(directory) / "request.json"
            with self.assertRaises(IntegrationTimeoutError):
                read_json_message(missing, timeout=0.03)

    def test_delayed_file_is_received_before_timeout(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "request.json"

            def create_file():
                time.sleep(0.02)
                write_json_message(path, build_request(self.matrix, request_id="delayed"))

            writer = Thread(target=create_file)
            writer.start()
            message = read_json_message(path, timeout=0.5)
            writer.join()
        self.assertEqual(message["request_id"], "delayed")

    def test_malformed_json_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "request.json"
            path.write_text("{broken", encoding="utf-8")
            with self.assertRaises(InvalidMessageError):
                read_json_message(path)

    def test_non_object_json_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "request.json"
            path.write_text("[]", encoding="utf-8")
            with self.assertRaises(InvalidMessageError):
                read_json_message(path)

    def test_json_is_written_in_utf8(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "message.json"
            write_json_message(path, {"message": "готово"})
            self.assertEqual(json.loads(path.read_text(encoding="utf-8"))["message"], "готово")

    def test_writer_requires_object(self):
        with self.assertRaises(InvalidMessageError):
            write_json_message("message.json", [])

    def test_output_module_formats_response(self):
        response = integrate_request(build_request([[1, 2], [3, 4]], method="rows"))
        lines = []
        print_response(response, lines.append)
        self.assertIn("Исходная матрица:", lines)
        self.assertIn("Обмен диагоналей по строкам:", lines)
        self.assertEqual(format_matrix([[1.0, 2.5]]), "1 2.5")

    def test_output_module_formats_columns_and_errors(self):
        columns = integrate_request(build_request([[1, 2], [3, 4]], method="columns"))
        lines = []
        print_response(columns, lines.append)
        self.assertIn("Обмен диагоналей по столбцам:", lines)

        error_lines = []
        error_response = {"status": "error", "error": {"code": "x", "message": "ошибка"}}
        print_response(error_response, error_lines.append)
        self.assertIn("Ошибка интеграции [x]: ошибка", error_lines)
        with self.assertRaises(InvalidMessageError):
            print_response({"status": "unknown"})

    def test_matrix_validation_rejects_non_numeric_values(self):
        for matrix in [[[True]], [[float("inf")]], [["1"]]]:
            with self.assertRaises(ValueError):
                validate_square_matrix(matrix)

    def test_main_processes_json_files(self):
        with tempfile.TemporaryDirectory() as directory:
            request_path = Path(directory) / "request.json"
            response_path = Path(directory) / "response.json"
            write_json_message(request_path, build_request([[1]], request_id="cli"))
            response = main(["--request", str(request_path), "--response", str(response_path)])
        self.assertEqual(response["status"], "ok")

    def test_interactive_mode_connects_all_modules(self):
        with patch("src.main.read_size", return_value=1), patch(
            "src.main.read_matrix", return_value=[[5.0]]
        ), patch("src.main.print_response") as printer:
            run_interactive()
        self.assertEqual(printer.call_count, 1)


if __name__ == "__main__":
    unittest.main()
