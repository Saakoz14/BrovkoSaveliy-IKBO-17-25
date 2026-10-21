"""Сравнение версий и обработка диапазонов NuGet.

Файл разбирает обычные и предварительные версии, проверяет ограничения и
выбирает максимальную подходящую версию зависимости.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from functools import total_ordering


VERSION_PATTERN = re.compile(
    r"^(\d+(?:\.\d+){0,3})(?:-([0-9A-Za-z.-]+))?(?:\+[0-9A-Za-z.-]+)?$"
)


class VersionError(Exception):
    """Ошибка разбора или выбора версии."""


@total_ordering
@dataclass(frozen=True, eq=False)
class NuGetVersion:
    """Сравнимая версия пакета NuGet."""

    original: str
    numbers: tuple[int, ...]
    prerelease: tuple[tuple[int, object], ...] | None

    @classmethod
    def parse(cls, value: str) -> "NuGetVersion":
        """Разобрать строковое представление версии."""
        match = VERSION_PATTERN.fullmatch(value.strip())
        if match is None:
            raise VersionError(f"некорректная версия NuGet: {value!r}")
        numbers = tuple(int(part) for part in match.group(1).split("."))
        numbers += (0,) * (4 - len(numbers))
        prerelease = _parse_prerelease(match.group(2))
        return cls(value.strip(), numbers, prerelease)

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, NuGetVersion):
            return NotImplemented
        if self.numbers != other.numbers:
            return self.numbers < other.numbers
        if self.prerelease is None:
            return False
        if other.prerelease is None:
            return True
        return self.prerelease < other.prerelease

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, NuGetVersion):
            return NotImplemented
        return (
            self.numbers,
            self.prerelease,
        ) == (
            other.numbers,
            other.prerelease,
        )

    def __hash__(self) -> int:
        return hash((self.numbers, self.prerelease))


def select_version(versions: list[str], specification: str) -> str:
    """Выбрать максимальную версию, допустимую диапазоном NuGet."""
    parsed = [NuGetVersion.parse(version) for version in versions]
    candidates = [
        version for version in parsed
        if _matches(version, specification)
    ]
    if "-" not in specification:
        stable = [item for item in candidates if item.prerelease is None]
        candidates = stable or candidates
    if not candidates:
        raise VersionError(
            f"нет версии, подходящей под ограничение {specification!r}"
        )
    return max(candidates).original


def _matches(version: NuGetVersion, specification: str) -> bool:
    spec = specification.strip()
    if not spec or spec == "*":
        return True
    if spec.startswith("[") and spec.endswith("]") and "," not in spec:
        return version == NuGetVersion.parse(spec[1:-1])
    if spec[0:1] in {"[", "("} and spec[-1:] in {"]", ")"}:
        return _matches_range(version, spec)
    return version >= NuGetVersion.parse(spec)


def _matches_range(version: NuGetVersion, specification: str) -> bool:
    lower_text, upper_text = specification[1:-1].split(",", maxsplit=1)
    if lower_text:
        lower = NuGetVersion.parse(lower_text)
        if version < lower or (version == lower and specification[0] == "("):
            return False
    if upper_text:
        upper = NuGetVersion.parse(upper_text)
        if version > upper or (version == upper and specification[-1] == ")"):
            return False
    return True


def _parse_prerelease(
    value: str | None,
) -> tuple[tuple[int, object], ...] | None:
    if value is None:
        return None
    result: list[tuple[int, object]] = []
    for part in value.split("."):
        if part.isdigit():
            result.append((0, int(part)))
        else:
            result.append((1, part.lower()))
    return tuple(result)

