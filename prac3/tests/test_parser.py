"""Тесты CSV-парсера ассемблера."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src.assembler import format_instruction
from src.parser import AssemblyError, parse_program


def write_source(directory: Path, content: str) -> Path:
    """Создать временную исходную программу."""
    path = directory / "program.csv"
    path.write_text(content, encoding="utf-8")
    return path


class ParserTest(unittest.TestCase):
    """Проверка промежуточного представления команд."""

    def test_parses_all_commands(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = write_source(
                Path(temporary),
                "mnemonic,b,c,d\n"
                "load_const,541,480,\n"
                "read,162,986,494\n"
                "write,894,643,71\n"
                "mod,860,700,606\n",
            )
            instructions = parse_program(path)
        self.assertEqual(len(instructions), 4)
        self.assertEqual(
            format_instruction(instructions[0]),
            "load_const: A=18, B=541, C=480",
        )

    def test_rejects_unknown_command(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = write_source(
                Path(temporary),
                "mnemonic,b,c,d\nmissing,1,2,\n",
            )
            with self.assertRaisesRegex(AssemblyError, "неизвестная команда"):
                parse_program(path)

    def test_rejects_out_of_range_field(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = write_source(
                Path(temporary),
                "mnemonic,b,c,d\nread,1024,1,1\n",
            )
            with self.assertRaisesRegex(AssemblyError, "вне диапазона"):
                parse_program(path)


if __name__ == "__main__":
    unittest.main()
