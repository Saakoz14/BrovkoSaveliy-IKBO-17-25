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
from .visualization import save_graph_svg


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
        root = PackageRef(config.package_name, config.package_version)
        graph = build_graph_bfs(
            repository=repository,
            root=root,
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
    output_path = Path(__file__).resolve().parents[1] / "output"
    image_path = save_graph_svg(
        graph,
        root,
        output_path / "dependency_graph.svg",
    )
    print(f"Изображение графа сохранено: {image_path}")
    return 0


def create_repository(config: AppConfig) -> DependencyRepository:
    """Создать реальный или тестовый источник зависимостей."""
    if config.test_mode:
        return TestRepository(Path(config.repository))
    return NuGetRepository(config.repository)


if __name__ == "__main__":
    sys.exit(main())
