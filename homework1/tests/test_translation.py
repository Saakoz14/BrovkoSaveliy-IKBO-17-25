"""Интеграционные тесты перевода конфигураций в TOML."""

from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

from src.main import translate


PROJECT_DIRECTORY = Path(__file__).resolve().parents[1]
EXAMPLE_NAMES = ("web_server", "database", "game")


class TranslationTest(unittest.TestCase):
    """Проверка примеров и поведения CLI."""

    def test_translates_three_domain_examples(self) -> None:
        """Три предметных примера совпадают с эталонным TOML."""
        for name in EXAMPLE_NAMES:
            source_path = PROJECT_DIRECTORY / "examples" / f"{name}.conf"
            expected_path = (
                PROJECT_DIRECTORY
                / "examples"
                / "expected"
                / f"{name}.toml"
            )
            source = source_path.read_text(encoding="utf-8")
            expected = expected_path.read_text(encoding="utf-8")
            self.assertEqual(translate(source), expected)

    def test_cli_uses_standard_streams(self) -> None:
        """CLI принимает stdin и возвращает TOML через stdout."""
        result = subprocess.run(
            [sys.executable, "-m", "src.main"],
            input="global answer = 42",
            text=True,
            capture_output=True,
            cwd=PROJECT_DIRECTORY,
            check=False,
        )
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "answer = 42\n")
        self.assertEqual(result.stderr, "")

    def test_cli_reports_syntax_error(self) -> None:
        """CLI пишет ошибку в stderr и возвращает ненулевой код."""
        result = subprocess.run(
            [sys.executable, "-m", "src.main"],
            input="global broken = dict(value 1)",
            text=True,
            capture_output=True,
            cwd=PROJECT_DIRECTORY,
            check=False,
        )
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, "")
        self.assertIn("Ошибка:", result.stderr)


if __name__ == "__main__":
    unittest.main()

