"""Модели синтаксического дерева конфигурационного языка."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Union


@dataclass(frozen=True)
class ConstantReference:
    """Ссылка на константу, вычисляемую при трансляции."""

    name: str


RawValue = Union[
    int,
    Dict[str, "RawValue"],
    ConstantReference,
]


@dataclass(frozen=True)
class Declaration:
    """Глобальное объявление имени и его исходного значения."""

    name: str
    value: RawValue


ResolvedValue = Union[int, Dict[str, "ResolvedValue"]]

