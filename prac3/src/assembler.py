"""CLI-приложение ассемблера учебной виртуальной машины."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence

from .model import Instruction
from .parser import AssemblyError, parse_program
from .specification import COMMANDS


def build_parser() -> argparse.ArgumentParser:
    """Создать парсер аргументов командной строки."""
    parser = argparse.ArgumentParser(description="Ассемблер УВМ, вариант 5")
    parser.add_argument("source", type=Path, help="исходная CSV-программа")
    parser.add_argument("output", type=Path, help="выходной бинарный файл")
    parser.add_argument(
        "--test",
        action="store_true",
        help="вывести промежуточное представление",
    )
    return parser


def format_instruction(instruction: Instruction) -> str:
    """Представить команду как набор полей и значений."""
    spec = COMMANDS[instruction.mnemonic]
    fields = [f"A={spec.opcode}"]
    fields.extend(
        f"{field.name}={value}"
        for field, value in zip(spec.fields, instruction.operands)
    )
    return f"{instruction.mnemonic}: " + ", ".join(fields)


def main(arguments: Sequence[str] | None = None) -> int:
    """Разобрать исходную программу и показать результат в тестовом режиме."""
    options = build_parser().parse_args(arguments)
    try:
        instructions = parse_program(options.source)
    except AssemblyError as error:
        print(f"Ошибка ассемблирования: {error}", file=sys.stderr)
        return 1
    print(f"Распознано команд: {len(instructions)}")
    if options.test:
        print("Промежуточное представление:")
        for instruction in instructions:
            print(format_instruction(instruction))
    return 0


if __name__ == "__main__":
    sys.exit(main())

