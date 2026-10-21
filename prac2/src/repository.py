"""Общий интерфейс источника зависимостей.

Протокол позволяет алгоритму BFS одинаково работать с настоящим NuGet и
локальным тестовым CSV-репозиторием.
"""

from typing import Protocol

from .models import Dependency


class DependencyRepository(Protocol):
    """Операции, необходимые алгоритму построения графа."""

    def get_direct_dependencies(
        self, package_name: str, package_version: str
    ) -> list[Dependency]:
        """Получить непосредственные зависимости пакета."""

    def resolve_version(self, package_name: str, version_spec: str) -> str:
        """Выбрать конкретную версию зависимости."""

