"""Чтение и проверка CSV-конфигурации приложения.

Файл преобразует пары ``key,value`` в объект ``AppConfig`` и сообщает об
ошибках имён, версий, глубины, режима и адреса репозитория.
"""

from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse


CONFIG_KEYS = {
    "package_name",
    "repository",
    "test_mode",
    "package_version",
    "max_depth",
    "filter_substring",
}
PACKAGE_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
VERSION_PATTERN = re.compile(
    r"^\d+(?:\.\d+){0,3}(?:[-+][0-9A-Za-z.-]+)?$"
)


class ConfigError(Exception):
    """Ошибка конфигурационного файла."""


@dataclass(frozen=True)
class AppConfig:
    """Проверенные параметры приложения."""

    package_name: str
    repository: str
    test_mode: bool
    package_version: str
    max_depth: int
    filter_substring: str

    def as_pairs(self) -> list[tuple[str, str]]:
        """Вернуть параметры в формате ключ-значение."""
        return [
            ("package_name", self.package_name),
            ("repository", self.repository),
            ("test_mode", str(self.test_mode).lower()),
            ("package_version", self.package_version),
            ("max_depth", str(self.max_depth)),
            ("filter_substring", self.filter_substring),
        ]


def load_config(path: Path) -> AppConfig:
    """Прочитать и проверить конфигурационный CSV-файл."""
    values = _read_values(path)
    missing = CONFIG_KEYS - values.keys()
    unknown = values.keys() - CONFIG_KEYS
    if missing:
        names = ", ".join(sorted(missing))
        raise ConfigError(f"отсутствуют параметры: {names}")
    if unknown:
        names = ", ".join(sorted(unknown))
        raise ConfigError(f"неизвестные параметры: {names}")
    test_mode = _parse_bool(values["test_mode"])
    repository = _validate_repository(
        values["repository"], test_mode, path.parent
    )
    return AppConfig(
        package_name=_validate_package(values["package_name"]),
        repository=repository,
        test_mode=test_mode,
        package_version=_validate_version(values["package_version"]),
        max_depth=_parse_depth(values["max_depth"]),
        filter_substring=values["filter_substring"].strip(),
    )


def _read_values(path: Path) -> dict[str, str]:
    if not path.is_file():
        raise ConfigError(f"файл конфигурации не найден: {path}")
    try:
        with path.open(encoding="utf-8-sig", newline="") as stream:
            reader = csv.DictReader(stream)
            if reader.fieldnames != ["key", "value"]:
                raise ConfigError("заголовок CSV должен быть: key,value")
            return _rows_to_values(reader)
    except (OSError, csv.Error) as error:
        raise ConfigError(f"не удалось прочитать CSV: {error}") from error


def _rows_to_values(reader: csv.DictReader) -> dict[str, str]:
    values: dict[str, str] = {}
    for line_number, row in enumerate(reader, start=2):
        key = (row.get("key") or "").strip()
        value = row.get("value")
        if not key or value is None:
            raise ConfigError(f"некорректная строка CSV: {line_number}")
        if key in values:
            raise ConfigError(f"параметр указан повторно: {key}")
        values[key] = value.strip()
    return values


def _validate_package(value: str) -> str:
    package = value.strip()
    if not PACKAGE_PATTERN.fullmatch(package):
        raise ConfigError(f"некорректное имя пакета: {value!r}")
    return package


def _validate_version(value: str) -> str:
    version = value.strip()
    if not VERSION_PATTERN.fullmatch(version):
        raise ConfigError(f"некорректная версия пакета: {value!r}")
    return version


def _parse_bool(value: str) -> bool:
    normalized = value.strip().lower()
    if normalized not in {"true", "false"}:
        raise ConfigError("test_mode должен иметь значение true или false")
    return normalized == "true"


def _parse_depth(value: str) -> int:
    try:
        depth = int(value)
    except ValueError as error:
        raise ConfigError("max_depth должен быть целым числом") from error
    if depth < 0:
        raise ConfigError("max_depth не может быть отрицательным")
    return depth


def _validate_repository(
    value: str, test_mode: bool, base_directory: Path
) -> str:
    repository = value.strip()
    if not repository:
        raise ConfigError("repository не может быть пустым")
    if test_mode:
        path = Path(repository).expanduser()
        if not path.is_absolute():
            path = base_directory / path
        if not path.is_file():
            raise ConfigError(f"тестовый репозиторий не найден: {path}")
        return str(path.resolve())
    parsed = urlparse(repository)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ConfigError("repository должен быть URL с http или https")
    return repository.rstrip("/")

