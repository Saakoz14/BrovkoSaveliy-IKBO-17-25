"""Разбор CSV-языка ассемблера."""

from __future__ import annotations

import csv
from pathlib import Path

from .model import Instruction
from .specification import COMMANDS


CSV_COLUMNS = ["mnemonic", "b", "c", "d"]


class AssemblyError(Exception):
    """Ошибка исходной программы."""


def parse_program(path: Path) -> list[Instruction]:
    """Прочитать и проверить CSV-программу."""
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
        message = f"не удалось прочитать CSV: {error}"
        raise AssemblyError(message) from error
    if not instructions:
        raise AssemblyError("программа не содержит команд")
    return instructions


def _parse_row(row: dict[str, str | None], line_number: int) -> Instruction:
    """Преобразовать одну CSV-строку в команду."""
    mnemonic = (row.get("mnemonic") or "").strip().lower()
    if mnemonic not in COMMANDS:
        message = (
            f"строка {line_number}: неизвестная команда "
            f"{mnemonic!r}"
        )
        raise AssemblyError(message)
    spec = COMMANDS[mnemonic]
    cells = [(row.get(name) or "").strip() for name in ("b", "c", "d")]
    expected_count = len(spec.fields)
    if any(cells[index] for index in range(expected_count, 3)):
        message = f"строка {line_number}: у команды {mnemonic} лишние поля"
        raise AssemblyError(message)
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
    """Прочитать числовое поле и проверить его диапазон."""
    if not text:
        raise AssemblyError(
            f"строка {line_number}: отсутствует поле {field_name}"
        )
    try:
        value = int(text, 0)
    except ValueError as error:
        message = (
            f"строка {line_number}: поле {field_name} "
            "не является числом"
        )
        raise AssemblyError(message) from error
    if not 0 <= value <= maximum:
        message = (
            f"строка {line_number}: поле {field_name} "
            f"вне диапазона 0..{maximum}"
        )
        raise AssemblyError(message)
    return value

