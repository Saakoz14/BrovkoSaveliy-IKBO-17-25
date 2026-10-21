"""Модели пакетов и зависимостей.

Файл содержит неизменяемые структуры ``Dependency`` и ``PackageRef``,
которыми обмениваются репозитории и алгоритм построения графа.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Dependency:
    """Зависимость и ограничение её версии."""

    name: str
    version_spec: str


@dataclass(frozen=True)
class PackageRef:
    """Ссылка на пакет с конкретной версией."""

    name: str
    version: str

    def label(self) -> str:
        """Вернуть короткую подпись пакета."""
        return f"{self.name}@{self.version}"

