"""Интерактивный режим эмулятора."""

from __future__ import annotations

import getpass
import shlex
import socket
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import TextIO

from .vfs import VirtualFileSystem


class CommandError(Exception):
    """Ошибка команды эмулятора."""


@dataclass(frozen=True)
class ScriptResult:
    """Результат стартового скрипта."""

    success: bool
    exit_requested: bool = False


class Shell:
    """Простой REPL с командами-заглушками."""

    def __init__(
        self,
        output: TextIO | None = None,
        vfs: VirtualFileSystem | None = None,
    ) -> None:
        self.output = output or sys.stdout
        self.vfs = vfs

    @staticmethod
    def parse(line: str) -> list[str]:
        """Разобрать строку с учётом кавычек."""
        try:
            return shlex.split(line, comments=True, posix=True)
        except ValueError as error:
            message = f"ошибка разбора: {error}"
            raise CommandError(message) from error

    def execute(self, line: str) -> bool:
        """Выполнить команду и сообщить о запросе выхода."""
        parts = self.parse(line)
        if not parts:
            return False
        command, arguments = parts[0], parts[1:]
        if command == "ls":
            self._print_stub(command, arguments)
        elif command == "cd":
            self._execute_cd(arguments)
        elif command == "exit":
            return self._execute_exit(arguments)
        else:
            message = f"неизвестная команда: {command}"
            raise CommandError(message)
        return False

    def run_repl(self) -> None:
        """Читать команды до получения exit."""
        while True:
            try:
                line = input(self.build_prompt())
                if self.execute(line):
                    return
            except CommandError as error:
                self._write_error(error)
            except (EOFError, KeyboardInterrupt):
                self.output.write("\n")
                return

    def run_script(self, path: Path) -> ScriptResult:
        """Выполнить скрипт до выхода или первой ошибки."""
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except OSError as error:
            message = CommandError(
                f"не удалось прочитать скрипт: {error}"
            )
            self._write_error(message)
            return ScriptResult(success=False)
        for line_number, raw_line in enumerate(lines, start=1):
            line = raw_line.strip()
            if not self.parse(line):
                continue
            self.output.write(f"$ {line}\n")
            result = self._run_script_line(line, line_number)
            if result is not None:
                return result
        return ScriptResult(success=True)

    def _run_script_line(
        self, line: str, line_number: int
    ) -> ScriptResult | None:
        try:
            if self.execute(line):
                return ScriptResult(success=True, exit_requested=True)
        except CommandError as error:
            message = CommandError(f"строка {line_number}: {error}")
            self._write_error(message)
            return ScriptResult(success=False)
        return None

    @staticmethod
    def build_prompt() -> str:
        """Создать приглашение из данных ОС."""
        user = getpass.getuser()
        hostname = socket.gethostname().split(".", maxsplit=1)[0]
        current_directory = Shell._short_current_directory()
        return f"{user}@{hostname}:{current_directory}$ "

    @staticmethod
    def _short_current_directory() -> str:
        current = Path.cwd()
        home = Path.home()
        try:
            relative = current.relative_to(home)
        except ValueError:
            return str(current)
        return "~" if not relative.parts else f"~/{relative}"

    def _execute_cd(self, arguments: list[str]) -> None:
        if len(arguments) > 1:
            message = "cd: ожидался ноль или один аргумент"
            raise CommandError(message)
        self._print_stub("cd", arguments)

    @staticmethod
    def _execute_exit(arguments: list[str]) -> bool:
        if arguments:
            message = "exit: команда не принимает аргументы"
            raise CommandError(message)
        return True

    def _print_stub(self, command: str, arguments: list[str]) -> None:
        self.output.write(f"команда: {command}\n")
        self.output.write(f"аргументы: {arguments}\n")

    def _write_error(self, error: CommandError) -> None:
        self.output.write(f"ошибка: {error}\n")
