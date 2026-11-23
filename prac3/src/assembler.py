"""CLI-приложение ассемблера УВМ."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence

from .encoder import assemble_program, encode_instruction, format_bytes
from .model import Instruction
from .parser import AssemblyError, parse_program
from .specification import COMMANDS


def build_parser() -> argparse.ArgumentParser:
    """Создать парсер аргументов CLI."""
    parser = argparse.ArgumentParser(
        description="Ассемблер УВМ, вариант 5"
    )
    parser.add_argument(
        "source",
        type=Path,
        help="исходная CSV-программа",
    )
    parser.add_argument(
        "output",
        type=Path,
        help="выходной бинарный файл",
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="вывести промежуточное представление",
    )
    return parser


def format_instruction(instruction: Instruction) -> str:
    """Представить команду набором полей."""
    spec = COMMANDS[instruction.mnemonic]
    fields = [f"A={spec.opcode}"]
    fields.extend(
        f"{field.name}={value}"
        for field, value in zip(spec.fields, instruction.operands)
    )
    return f"{instruction.mnemonic}: " + ", ".join(fields)


def main(arguments: Sequence[str] | None = None) -> int:
    """Разобрать и записать машинный код."""
    options = build_parser().parse_args(arguments)
    try:
        instructions = parse_program(options.source)
        machine_code = assemble_program(instructions)
        options.output.parent.mkdir(parents=True, exist_ok=True)
        options.output.write_bytes(machine_code)
    except (AssemblyError, OSError) as error:
        print(f"Ошибка ассемблирования: {error}", file=sys.stderr)
        return 1
    print(f"Распознано команд: {len(instructions)}")
    print(f"Размер двоичного файла: {len(machine_code)} байт")
    if options.test:
        print("Промежуточное представление:")
        for instruction in instructions:
            print(format_instruction(instruction))
        print("Машинный код:")
        for instruction in instructions:
            print(format_bytes(encode_instruction(instruction)))
    return 0


if __name__ == "__main__":
    sys.exit(main())

