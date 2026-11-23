"""Интерпретатор и модель памяти УВМ."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path
from typing import Sequence

from .encoder import decode_instruction
from .model import Instruction
from .parser import AssemblyError
from .specification import INSTRUCTION_SIZE, MEMORY_SIZE


class ExecutionError(Exception):
    """Ошибка выполнения машинной программы."""


class VirtualMachine:
    """УВМ с раздельной памятью команд и данных."""

    def __init__(self, memory_size: int = MEMORY_SIZE) -> None:
        """Создать пустую память команд и данных."""
        self.instruction_memory = b""
        self.data_memory = [0] * memory_size

    def load_program(self, machine_code: bytes) -> None:
        """Загрузить программу в память команд."""
        if len(machine_code) % INSTRUCTION_SIZE != 0:
            message = "размер программы должен быть кратен размеру команды"
            raise ExecutionError(message)
        self.instruction_memory = bytes(machine_code)

    def run(self) -> None:
        """Декодировать и выполнить команды."""
        for offset in range(0, len(self.instruction_memory), INSTRUCTION_SIZE):
            machine_code = self.instruction_memory[
                offset:offset + INSTRUCTION_SIZE
            ]
            try:
                instruction = decode_instruction(machine_code)
            except AssemblyError as error:
                message = f"ошибка команды по смещению {offset}: {error}"
                raise ExecutionError(message) from error
            self.execute(instruction)

    def execute(self, instruction: Instruction) -> None:
        """Выполнить одну базовую команду УВМ."""
        if instruction.mnemonic == "load_const":
            address, constant = instruction.operands
            self._write(address, constant)
            return
        if instruction.mnemonic == "read":
            displacement, pointer_address, destination = instruction.operands
            source = self._read(pointer_address) + displacement
            self._write(destination, self._read(source))
            return
        if instruction.mnemonic == "write":
            source, pointer_address, displacement = instruction.operands
            destination = self._read(pointer_address) + displacement
            self._write(destination, self._read(source))
            return
        if instruction.mnemonic == "mod":
            divisor_address, destination, pointer_address = instruction.operands
            dividend_address = self._read(pointer_address)
            divisor = self._read(divisor_address)
            if divisor == 0:
                raise ExecutionError("деление с остатком на ноль")
            self._write(
                destination,
                self._read(dividend_address) % divisor,
            )
            return
        message = f"команда {instruction.mnemonic} пока не поддерживается"
        raise ExecutionError(message)

    def _read(self, address: int) -> int:
        """Прочитать ячейку с проверкой адреса."""
        self._validate_address(address)
        return self.data_memory[address]

    def _write(self, address: int, value: int) -> None:
        """Записать значение с проверкой адреса."""
        self._validate_address(address)
        self.data_memory[address] = value

    def _validate_address(self, address: int) -> None:
        """Проверить попадание адреса в память данных."""
        if not 0 <= address < len(self.data_memory):
            message = f"адрес памяти вне диапазона: {address}"
            raise ExecutionError(message)

    def save_dump(self, path: Path, start: int, end: int) -> None:
        """Сохранить диапазон памяти в CSV-файл."""
        if start > end:
            message = "начало дампа не может быть больше конца"
            raise ExecutionError(message)
        self._validate_address(start)
        self._validate_address(end)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow(["address", "value"])
            writer.writerows(
                (address, self.data_memory[address])
                for address in range(start, end + 1)
            )


def build_parser() -> argparse.ArgumentParser:
    """Создать парсер аргументов интерпретатора."""
    parser = argparse.ArgumentParser(description="Интерпретатор УВМ")
    parser.add_argument(
        "program",
        type=Path,
        help="бинарная программа",
    )
    parser.add_argument("dump", type=Path, help="выходной CSV-дамп")
    parser.add_argument("--start", type=int, required=True)
    parser.add_argument("--end", type=int, required=True)
    return parser


def main(arguments: Sequence[str] | None = None) -> int:
    """Выполнить программу и сохранить дамп."""
    options = build_parser().parse_args(arguments)
    try:
        machine = VirtualMachine()
        machine.load_program(options.program.read_bytes())
        machine.run()
        machine.save_dump(options.dump, options.start, options.end)
    except (OSError, ExecutionError) as error:
        print(f"Ошибка выполнения: {error}", file=sys.stderr)
        return 1
    command_count = len(machine.instruction_memory) // INSTRUCTION_SIZE
    print(f"Выполнено команд: {command_count}")
    print(f"Дамп памяти сохранён: {options.dump}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

