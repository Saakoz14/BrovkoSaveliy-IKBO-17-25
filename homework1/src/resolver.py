"""Вычисление констант учебного конфигурационного языка."""

from __future__ import annotations

from .errors import ConfigLanguageError
from .models import (
    ConstantReference,
    Declaration,
    RawValue,
    ResolvedValue,
)


class ConstantResolver:
    """Вычисление ссылок с обнаружением ошибок и циклов."""

    def __init__(self, declarations: list[Declaration]) -> None:
        """Сохранить объявления и проверить уникальность имён."""
        self._raw: dict[str, RawValue] = {}
        self._resolved: dict[str, ResolvedValue] = {}
        self._active: set[str] = set()
        for declaration in declarations:
            if declaration.name in self._raw:
                message = (
                    "повторное объявление константы: "
                    f"{declaration.name}"
                )
                raise ConfigLanguageError(message)
            self._raw[declaration.name] = declaration.value

    def resolve_all(self) -> dict[str, ResolvedValue]:
        """Вычислить все глобальные значения."""
        return {
            name: self._resolve_name(name)
            for name in self._raw
        }

    def _resolve_name(self, name: str) -> ResolvedValue:
        """Вычислить одно имя с мемоизацией результата."""
        if name in self._resolved:
            return self._resolved[name]
        if name not in self._raw:
            message = f"неизвестная константа: {name}"
            raise ConfigLanguageError(message)
        if name in self._active:
            message = f"циклическая ссылка на константу: {name}"
            raise ConfigLanguageError(message)
        return self._resolve_new_name(name)

    def _resolve_new_name(self, name: str) -> ResolvedValue:
        """Вычислить ещё не обработанное имя."""
        self._active.add(name)
        try:
            value = self._resolve_value(self._raw[name])
        finally:
            self._active.remove(name)
        self._resolved[name] = value
        return value

    def _resolve_value(self, value: RawValue) -> ResolvedValue:
        """Рекурсивно вычислить число, ссылку или словарь."""
        if isinstance(value, int):
            return value
        if isinstance(value, ConstantReference):
            return self._resolve_name(value.name)
        return {
            name: self._resolve_value(item)
            for name, item in value.items()
        }


def resolve_constants(
    declarations: list[Declaration],
) -> dict[str, ResolvedValue]:
    """Вычислить константы из списка объявлений."""
    return ConstantResolver(declarations).resolve_all()

