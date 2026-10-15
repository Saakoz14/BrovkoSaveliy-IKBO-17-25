"""Запуск эмулятора и обработка параметров."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence

from .shell import Shell
from .vfs import VfsError, VirtualFileSystem


def build_argument_parser() -> argparse.ArgumentParser:
    """Создать парсер параметров запуска."""
    parser = argparse.ArgumentParser(
        description="Эмулятор командной оболочки"
    )
    parser.add_argument(
        "--vfs",
        type=Path,
        help="путь к директории VFS",
    )
    parser.add_argument(
        "--script",
        type=Path,
        help="путь к стартовому скрипту",
    )
    return parser


def main(arguments: Sequence[str] | None = None) -> int:
    """Прочитать настройки и запустить эмулятор."""
    options = build_argument_parser().parse_args(arguments)
    print("Конфигурация эмулятора:")
    print(f"  vfs: {options.vfs or '(не задано)'}")
    print(f"  script: {options.script or '(не задано)'}")
    try:
        vfs = load_vfs(options.vfs)
    except VfsError as error:
        print(f"ошибка загрузки VFS: {error}", file=sys.stderr)
        return 2
    shell = Shell(vfs=vfs)
    if options.script is not None:
        result = shell.run_script(options.script)
        if not result.success:
            return 1
        if result.exit_requested:
            return 0
    shell.run_repl()
    return 0


def load_vfs(path: Path | None) -> VirtualFileSystem | None:
    """Загрузить VFS и вывести её параметры."""
    if path is None:
        return None
    vfs = VirtualFileSystem.from_directory(path)
    print(
        "VFS загружена: "
        f"{vfs.name} "
        f"(каталогов: {vfs.directory_count}, "
        f"файлов: {vfs.file_count}, байт: {vfs.total_size})"
    )
    return vfs


if __name__ == "__main__":
    sys.exit(main())

'''
# 1. Перейти в папку проекта
cd "/Users/lkzz/PycharmProjects/PythonProject1/practice1"

# 2. Обычный интерактивный запуск
./run.sh --vfs examples/vfs_nested

# Команды вводятся вручную:
# ls
# cd "level1"
# exit


# 3. Автоматический запуск со стартовым скриптом
./scripts/run_nested_vfs.sh


# 4. Запуск с минимальной VFS
./scripts/run_minimal_vfs.sh


# 5. Запуск с несколькими файлами в VFS
./scripts/run_multiple_vfs.sh


# 6. Проверка неизвестной команды
./scripts/run_with_error.sh


# 7. Проверка неправильных аргументов
./scripts/run_bad_arguments.sh


# 8. Проверка несуществующей VFS
./scripts/run_invalid_vfs.sh


# 9. Запуск всех автоматических тестов
python3 -m unittest discover -s tests -v


# 10. Если появилась ошибка Permission denied
chmod +x run.sh scripts/*.sh
'''