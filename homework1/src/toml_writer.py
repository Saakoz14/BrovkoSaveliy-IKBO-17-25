"""Формирование TOML из вычисленной конфигурации."""

from __future__ import annotations

from .models import ResolvedValue


def to_toml(values: dict[str, ResolvedValue]) -> str:
    """Преобразовать глобальные значения в текст TOML."""
    lines: list[str] = []
    _append_scalars(lines, values)
    for name, value in values.items():
        if isinstance(value, dict):
            _append_blank_line(lines)
            _append_table(lines, (name,), value)
    if not lines:
        return ""
    return "\n".join(lines) + "\n"


def _append_scalars(
    lines: list[str],
    values: dict[str, ResolvedValue],
) -> None:
    """Добавить числовые параметры текущего уровня."""
    for name, value in values.items():
        if isinstance(value, int):
            lines.append(f"{name} = {value}")


def _append_table(
    lines: list[str],
    path: tuple[str, ...],
    values: dict[str, ResolvedValue],
) -> None:
    """Добавить таблицу и все вложенные таблицы."""
    lines.append(f"[{'.'.join(path)}]")
    _append_scalars(lines, values)
    for name, value in values.items():
        if isinstance(value, dict):
            _append_blank_line(lines)
            _append_table(lines, path + (name,), value)


def _append_blank_line(lines: list[str]) -> None:
    """Отделить раздел TOML одной пустой строкой."""
    if lines and lines[-1]:
        lines.append("")

