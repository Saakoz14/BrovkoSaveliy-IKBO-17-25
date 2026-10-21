"""Локальный тестовый репозиторий зависимостей.

Файл читает описанный в CSV граф с пакетами A-Z и позволяет проверять
программу без подключения к настоящему NuGet.
"""

from __future__ import annotations

import csv
import re
from pathlib import Path

from .models import Dependency
from .versioning import VersionError, select_version


HEADERS = ["package", "version", "dependency", "dependency_version"]
TEST_PACKAGE_PATTERN = re.compile(r"^[A-Z]+$")


class TestRepositoryError(Exception):
    """Ошибка тестового репозитория."""


class TestRepository:
    """Граф пакетов, прочитанный из CSV-файла."""

    __test__ = False

    def __init__(self, path: Path) -> None:
        self.dependencies: dict[tuple[str, str], list[Dependency]] = {}
        self.versions: dict[str, set[str]] = {}
        self._load(path)

    def get_direct_dependencies(
        self, package_name: str, package_version: str
    ) -> list[Dependency]:
        """Получить зависимости заданного узла."""
        key = package_name, package_version
        if key not in self.dependencies:
            label = f"{package_name}@{package_version}"
            raise TestRepositoryError(f"пакет не найден: {label}")
        return list(self.dependencies[key])

    def resolve_version(self, package_name: str, version_spec: str) -> str:
        """Выбрать версию из тестового репозитория."""
        versions = sorted(self.versions.get(package_name, set()))
        if not versions:
            raise TestRepositoryError(f"пакет не найден: {package_name}")
        try:
            return select_version(versions, version_spec)
        except VersionError as error:
            raise TestRepositoryError(str(error)) from error

    def _load(self, path: Path) -> None:
        try:
            with path.open(encoding="utf-8-sig", newline="") as stream:
                reader = csv.DictReader(stream)
                if reader.fieldnames != HEADERS:
                    raise TestRepositoryError(
                        "заголовок тестового CSV должен быть: "
                        + ",".join(HEADERS)
                    )
                self._read_rows(reader)
        except (OSError, csv.Error) as error:
            message = f"не удалось прочитать тестовый репозиторий: {error}"
            raise TestRepositoryError(message) from error
        self._validate_targets()

    def _read_rows(self, reader: csv.DictReader) -> None:
        for line_number, row in enumerate(reader, start=2):
            package = (row.get("package") or "").strip()
            version = (row.get("version") or "").strip()
            dependency = (row.get("dependency") or "").strip()
            dependency_version = (
                row.get("dependency_version") or ""
            ).strip()
            self._validate_row(package, version, dependency, line_number)
            key = package, version
            self.dependencies.setdefault(key, [])
            self.versions.setdefault(package, set()).add(version)
            if dependency:
                item = Dependency(dependency, dependency_version or "*")
                if item not in self.dependencies[key]:
                    self.dependencies[key].append(item)

    @staticmethod
    def _validate_row(
        package: str, version: str, dependency: str, line_number: int
    ) -> None:
        if not TEST_PACKAGE_PATTERN.fullmatch(package):
            raise TestRepositoryError(
                f"строка {line_number}: имя пакета должно быть A-Z"
            )
        if dependency and not TEST_PACKAGE_PATTERN.fullmatch(dependency):
            raise TestRepositoryError(
                f"строка {line_number}: имя зависимости должно быть A-Z"
            )
        try:
            select_version([version], f"[{version}]")
        except VersionError as error:
            raise TestRepositoryError(
                f"строка {line_number}: {error}"
            ) from error

    def _validate_targets(self) -> None:
        for dependencies in self.dependencies.values():
            for dependency in dependencies:
                if dependency.name not in self.versions:
                    raise TestRepositoryError(
                        f"зависимый пакет не описан: {dependency.name}"
                    )

