"""Спецификация команд УВМ для варианта 5."""

from __future__ import annotations

from dataclasses import dataclass


INSTRUCTION_SIZE = 7
MEMORY_SIZE = 1 << 14


@dataclass(frozen=True)
class FieldSpec:
    """Положение и размер поля команды."""

    name: str
    shift: int
    width: int

    @property
    def maximum(self) -> int:
        """Вернуть максимальное значение поля."""
        return (1 << self.width) - 1


@dataclass(frozen=True)
class CommandSpec:
    """Код операции и набор её операндов."""

    mnemonic: str
    opcode: int
    fields: tuple[FieldSpec, ...]


COMMANDS = {
    "load_const": CommandSpec(
        "load_const",
        18,
        (FieldSpec("B", 5, 14), FieldSpec("C", 19, 32)),
    ),
    "read": CommandSpec(
        "read",
        5,
        (
            FieldSpec("B", 5, 10),
            FieldSpec("C", 15, 14),
            FieldSpec("D", 29, 14),
        ),
    ),
    "write": CommandSpec(
        "write",
        10,
        (
            FieldSpec("B", 5, 14),
            FieldSpec("C", 19, 14),
            FieldSpec("D", 33, 10),
        ),
    ),
    "mod": CommandSpec(
        "mod",
        1,
        (
            FieldSpec("B", 5, 14),
            FieldSpec("C", 19, 14),
            FieldSpec("D", 33, 14),
        ),
    ),
}

COMMANDS_BY_OPCODE = {spec.opcode: spec for spec in COMMANDS.values()}

