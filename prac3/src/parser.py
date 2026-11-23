"""Разбор CSV-языка ассемблера в промежуточное представление."""

from __future__ import annotations

import csv
from pathlib import Path

from .model import Instruction
from .specification import COMMANDS


CSV_COLUMNS = ["mnemonic", "b", "c", "d"]


class AssemblyError(Exception):
    """Ошибка исходной программы на языке ассемблера."""


def parse_program(path: Path) -> list[Instruction]:
    """Прочитать и проверить программу в формате CSV."""
    if not path.is_file():
        raise AssemblyError(f"исходный файл не найден: {path}")
    try:
        with path.open(encoding="utf-8-sig", newline="") as stream:
            reader = csv.DictReader(stream)
            if reader.fieldnames != CSV_COLUMNS:
                raise AssemblyError(
                    "заголовок CSV должен быть: mnemonic,b,c,d"
                )
            instructions = [
                _parse_row(row, line_number)
                for line_number, row in enumerate(reader, start=2)
            ]
    except (OSError, csv.Error) as error:
        raise AssemblyError(f"не удалось прочитать CSV: {error}") from error
    if not instructions:
        raise AssemblyError("программа не содержит команд")
    return instructions


def _parse_row(row: dict[str, str | None], line_number: int) -> Instruction:
    mnemonic = (row.get("mnemonic") or "").strip().lower()
    if mnemonic not in COMMANDS:
        raise AssemblyError(
            f"строка {line_number}: неизвестная команда {mnemonic!r}"
        )
    spec = COMMANDS[mnemonic]
    cells = [(row.get(name) or "").strip() for name in ("b", "c", "d")]
    expected_count = len(spec.fields)
    if any(cells[index] for index in range(expected_count, 3)):
        raise AssemblyError(
            f"строка {line_number}: у команды {mnemonic} лишние поля"
        )
    operands = tuple(
        _parse_operand(cells[index], field.maximum, line_number, field.name)
        for index, field in enumerate(spec.fields)
    )
    return Instruction(mnemonic, operands)


def _parse_operand(
    text: str,
    maximum: int,
    line_number: int,
    field_name: str,
) -> int:
    if not text:
        raise AssemblyError(
            f"строка {line_number}: отсутствует поле {field_name}"
        )
    try:
        value = int(text, 0)
    except ValueError as error:
        raise AssemblyError(
            f"строка {line_number}: поле {field_name} не является числом"
        ) from error
    if not 0 <= value <= maximum:
        raise AssemblyError(
            f"строка {line_number}: поле {field_name} вне диапазона "
            f"0..{maximum}"
        )
    return value

