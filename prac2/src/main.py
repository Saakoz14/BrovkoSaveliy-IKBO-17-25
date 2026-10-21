"""Точка входа инструмента анализа зависимостей."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence

from .config import AppConfig, ConfigError, load_config
from .graph import build_graph_bfs
from .models import PackageRef
from .nuget import NuGetError, NuGetRepository
from .repository import DependencyRepository
from .test_repository import TestRepository, TestRepositoryError


def build_parser() -> argparse.ArgumentParser:
    """Создать парсер аргументов командной строки."""
    parser = argparse.ArgumentParser(
        description="Анализ зависимостей пакетов NuGet"
    )
    parser.add_argument(
        "--config",
        required=True,
        type=Path,
        help="путь к CSV-конфигурации",
    )
    return parser


def main(arguments: Sequence[str] | None = None) -> int:
    """Загрузить настройки и построить граф зависимостей."""
    options = build_parser().parse_args(arguments)
    try:
        config = load_config(options.config)
        repository = create_repository(config)
        graph = build_graph_bfs(
            repository=repository,
            root=PackageRef(config.package_name, config.package_version),
            max_depth=config.max_depth,
            filter_substring=config.filter_substring,
        )
    except ConfigError as error:
        print(f"Ошибка конфигурации: {error}", file=sys.stderr)
        return 1
    except (NuGetError, TestRepositoryError) as error:
        print(f"Ошибка репозитория: {error}", file=sys.stderr)
        return 2
    print("Граф зависимостей:")
    for line in graph.format_lines():
        print(line)
    return 0


def create_repository(config: AppConfig) -> DependencyRepository:
    """Создать реальный или тестовый источник зависимостей."""
    if config.test_mode:
        return TestRepository(Path(config.repository))
    return NuGetRepository(config.repository)


if __name__ == "__main__":
    sys.exit(main())

'''
cd "/Users/lkzz/PycharmProjects/PythonProject1/practice2"

# Обычный транзитивный граф
./scripts/run_test_basic.sh

# Ограничение глубины
./scripts/run_test_depth.sh

# Циклические зависимости
./scripts/run_test_cycle.sh

# Фильтрация пакетов
./scripts/run_test_filter.sh

# Работа с настоящим NuGet
./scripts/run_live_nuget.sh

# Автоматические тесты
python3 -m unittest discover -s tests -v'''