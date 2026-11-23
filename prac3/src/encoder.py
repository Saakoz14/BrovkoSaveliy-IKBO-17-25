"""Кодирование 7-байтовых команд УВМ."""

from __future__ import annotations

from .model import Instruction
from .parser import AssemblyError
from .specification import COMMANDS, COMMANDS_BY_OPCODE, INSTRUCTION_SIZE


def encode_instruction(instruction: Instruction) -> bytes:
    """Закодировать одну команду."""
    spec = COMMANDS[instruction.mnemonic]
    value = spec.opcode
    for field, operand in zip(spec.fields, instruction.operands):
        if not 0 <= operand <= field.maximum:
            raise AssemblyError(
                f"поле {field.name} команды {instruction.mnemonic} "
                f"вне диапазона 0..{field.maximum}"
            )
        value |= operand << field.shift
    return value.to_bytes(INSTRUCTION_SIZE, byteorder="little")


def decode_instruction(machine_code: bytes) -> Instruction:
    """Декодировать одну машинную команду."""
    if len(machine_code) != INSTRUCTION_SIZE:
        raise AssemblyError(
            f"команда должна занимать {INSTRUCTION_SIZE} байт"
        )
    value = int.from_bytes(machine_code, byteorder="little")
    opcode = value & 0x1F
    if opcode not in COMMANDS_BY_OPCODE:
        raise AssemblyError(f"неизвестный код операции: {opcode}")
    spec = COMMANDS_BY_OPCODE[opcode]
    operands = tuple(
        (value >> field.shift) & field.maximum for field in spec.fields
    )
    return Instruction(spec.mnemonic, operands)


def assemble_program(instructions: list[Instruction]) -> bytes:
    """Собрать бинарную программу."""
    return b"".join(encode_instruction(item) for item in instructions)


def format_bytes(machine_code: bytes) -> str:
    """Представить байты шестнадцатеричными числами."""
    return ", ".join(f"0x{byte:02X}" for byte in machine_code)

