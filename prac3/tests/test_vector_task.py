"""Тесты итоговой задачи с векторами длины 7."""

from __future__ import annotations

import csv
import unittest
from pathlib import Path

from src.encoder import assemble_program
from src.interpreter import VirtualMachine
from src.parser import parse_program


PROJECT_DIRECTORY = Path(__file__).resolve().parents[1]


def read_expected(path: Path) -> list[int]:
    """Прочитать ожидаемый вектор из CSV-дампа."""
    with path.open(encoding="utf-8", newline="") as stream:
        return [int(row["value"]) for row in csv.DictReader(stream)]


class VectorTaskTest(unittest.TestCase):
    """Проверка трёх примеров вычисления остатка по модулю 213."""

    def check_example(self, name: str) -> None:
        """Собрать и выполнить один пример, затем сравнить результат."""
        source = PROJECT_DIRECTORY / "examples" / f"{name}.csv"
        expected_path = (
            PROJECT_DIRECTORY / "examples" / "expected" / f"{name}.csv"
        )
        instructions = parse_program(source)
        machine = VirtualMachine()
        machine.load_program(assemble_program(instructions))
        machine.run()
        self.assertEqual(
            machine.data_memory[200:207],
            read_expected(expected_path),
        )

    def test_first_vector(self) -> None:
        self.check_example("vector_mod_1")

    def test_second_vector(self) -> None:
        self.check_example("vector_mod_2")

    def test_third_vector(self) -> None:
        self.check_example("vector_mod_3")


if __name__ == "__main__":
    unittest.main()

