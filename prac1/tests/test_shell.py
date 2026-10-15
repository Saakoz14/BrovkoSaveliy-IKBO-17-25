"""Тесты первого этапа эмулятора."""

import io
import tempfile
import unittest
from pathlib import Path

from src.shell import CommandError, Shell


class ShellTest(unittest.TestCase):
    """Проверка парсера и команд-заглушек."""

    def setUp(self) -> None:
        self.output = io.StringIO()
        self.shell = Shell(output=self.output)

    def test_parser_preserves_quoted_argument(self) -> None:
        parts = self.shell.parse('ls "folder with spaces" file.txt')
        self.assertEqual(parts, ["ls", "folder with spaces", "file.txt"])

    def test_ls_prints_command_and_arguments(self) -> None:
        self.shell.execute("ls one two")
        self.assertIn("команда: ls", self.output.getvalue())
        self.assertIn("['one', 'two']", self.output.getvalue())

    def test_cd_rejects_extra_arguments(self) -> None:
        with self.assertRaises(CommandError):
            self.shell.execute("cd one two")

    def test_unknown_command_is_an_error(self) -> None:
        error = "неизвестная команда"
        with self.assertRaisesRegex(CommandError, error):
            self.shell.execute("missing")

    def test_exit_requests_shutdown(self) -> None:
        self.assertTrue(self.shell.execute("exit"))

    def test_exit_rejects_arguments(self) -> None:
        with self.assertRaises(CommandError):
            self.shell.execute("exit now")

    def test_startup_script_stops_after_first_error(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "startup.txt"
            path.write_text("ls one\nmissing\ncd skipped\n", encoding="utf-8")
            result = self.shell.run_script(path)
        self.assertFalse(result.success)
        self.assertIn("строка 2", self.output.getvalue())
        self.assertNotIn("skipped", self.output.getvalue())

    def test_startup_script_echoes_input_and_output(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "startup.txt"
            path.write_text('ls "two words"\nexit\n', encoding="utf-8")
            result = self.shell.run_script(path)
        self.assertTrue(result.success)
        self.assertTrue(result.exit_requested)
        self.assertIn('$ ls "two words"', self.output.getvalue())
        self.assertIn("two words", self.output.getvalue())


if __name__ == "__main__":
    unittest.main()
