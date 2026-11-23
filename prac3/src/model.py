"""Модели команд учебной виртуальной машины."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Instruction:
    """Команда после разбора исходного CSV-файла."""

    mnemonic: str
    operands: tuple[int, ...]

