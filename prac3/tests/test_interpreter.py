"""Тесты интерпретатора и операций с памятью."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src.encoder import assemble_program
from src.interpreter import ExecutionError, VirtualMachine
from src.model import Instruction


class InterpreterTest(unittest.TestCase):
    """Проверка базовых команд и CSV-дампа."""

    def test_copies_array_to_another_address(self) -> None:
        """Чтение и запись копируют массив."""
        instructions = [
            Instruction("load_const", (100, 11)),
            Instruction("load_const", (101, 22)),
            Instruction("load_const", (102, 33)),
            Instruction("load_const", (50, 100)),
            Instruction("load_const", (51, 200)),
        ]
        for index in range(3):
            instructions.extend(
                [
                    Instruction("read", (index, 50, 60)),
                    Instruction("write", (60, 51, index)),
                ]
            )
        machine = VirtualMachine()
        machine.load_program(assemble_program(instructions))
        machine.run()
        self.assertEqual(machine.data_memory[200:203], [11, 22, 33])

    def test_saves_selected_memory_range(self) -> None:
        """Дамп содержит только выбранный диапазон."""
        machine = VirtualMachine(memory_size=10)
        machine.data_memory[2:5] = [7, 8, 9]
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "dump.csv"
            machine.save_dump(path, 2, 4)
            content = path.read_text(encoding="utf-8")
        self.assertEqual(
            content.replace("\r\n", "\n"),
            "address,value\n2,7\n3,8\n4,9\n",
        )

    def test_calculates_modulo(self) -> None:
        """Команда остатка сохраняет правильный результат."""
        instructions = [
            Instruction("load_const", (100, 17)),
            Instruction("load_const", (200, 5)),
            Instruction("load_const", (50, 100)),
            Instruction("mod", (200, 300, 50)),
        ]
        machine = VirtualMachine()
        machine.load_program(assemble_program(instructions))
        machine.run()
        self.assertEqual(machine.data_memory[300], 2)

    def test_rejects_modulo_by_zero(self) -> None:
        """Остаток от деления на ноль запрещён."""
        instructions = [
            Instruction("load_const", (100, 17)),
            Instruction("load_const", (50, 100)),
            Instruction("mod", (200, 300, 50)),
        ]
        machine = VirtualMachine()
        machine.load_program(assemble_program(instructions))
        with self.assertRaisesRegex(ExecutionError, "на ноль"):
            machine.run()

    def test_rejects_invalid_program_size(self) -> None:
        """Неполная машинная команда отклоняется."""
        machine = VirtualMachine()
        with self.assertRaisesRegex(ExecutionError, "кратен"):
            machine.load_program(b"bad")


if __name__ == "__main__":
    unittest.main()
