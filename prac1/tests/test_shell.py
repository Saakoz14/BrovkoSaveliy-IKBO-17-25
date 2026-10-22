"""Тесты первого этапа эмулятора."""

import io
import tempfile
import unittest
from pathlib import Path

from src.shell import CommandError, Shell


class ShellTest(unittest.TestCase):
    """Проверка парсера и команд-заглушек."""

    def create_shell(self) -> tuple[Shell, io.StringIO]:
        """Создать оболочку и буфер для проверки её вывода."""
        output = io.StringIO()
        return Shell(output=output), output

    def test_parser_preserves_quoted_argument(self) -> None:
        shell, _ = self.create_shell()
        parts = shell.parse('ls "folder with spaces" file.txt')
        self.assertEqual(parts, ["ls", "folder with spaces", "file.txt"])

    def test_ls_prints_command_and_arguments(self) -> None:
        shell, output = self.create_shell()
        shell.execute("ls one two")
        self.assertIn("команда: ls", output.getvalue())
        self.assertIn("['one', 'two']", output.getvalue())

    def test_cd_rejects_extra_arguments(self) -> None:
        shell, _ = self.create_shell()
        with self.assertRaises(CommandError):
            shell.execute("cd one two")

    def test_unknown_command_is_an_error(self) -> None:
        shell, _ = self.create_shell()
        error = "неизвестная команда"
        with self.assertRaisesRegex(CommandError, error):
            shell.execute("missing")

    def test_exit_requests_shutdown(self) -> None:
        shell, _ = self.create_shell()
        self.assertTrue(shell.execute("exit"))

    def test_exit_rejects_arguments(self) -> None:
        shell, _ = self.create_shell()
        with self.assertRaises(CommandError):
            shell.execute("exit now")

    def test_startup_script_stops_after_first_error(self) -> None:
        shell, output = self.create_shell()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "startup.txt"
            path.write_text("ls one\nmissing\ncd skipped\n", encoding="utf-8")
            result = shell.run_script(path)
        self.assertFalse(result.success)
        self.assertIn("строка 2", output.getvalue())
        self.assertNotIn("skipped", output.getvalue())

    def test_startup_script_echoes_input_and_output(self) -> None:
        shell, output = self.create_shell()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "startup.txt"
            path.write_text('ls "two words"\nexit\n', encoding="utf-8")
            result = shell.run_script(path)
        self.assertTrue(result.success)
        self.assertTrue(result.exit_requested)
        self.assertIn('$ ls "two words"', output.getvalue())
        self.assertIn("two words", output.getvalue())


if __name__ == "__main__":
    unittest.main()
