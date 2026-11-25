"""Синтаксический анализ языка с помощью библиотеки Lark."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from lark import Lark, Transformer, UnexpectedInput
from lark.exceptions import VisitError

from .errors import ConfigLanguageError
from .models import ConstantReference, Declaration, RawValue


GRAMMAR_PATH = Path(__file__).with_name("grammar.lark")
GRAMMAR = GRAMMAR_PATH.read_text(encoding="utf-8")
LANGUAGE_PARSER = Lark(GRAMMAR, parser="lalr", start="start")


class ConfigTransformer(Transformer[Any, Any]):
    """Преобразование дерева Lark в модели приложения."""

    def start(self, items: list[Any]) -> list[Declaration]:
        """Собрать объявления верхнего уровня."""
        return list(items)

    def declaration(self, items: list[Any]) -> Declaration:
        """Создать глобальное объявление."""
        return Declaration(str(items[0]), items[1])

    def number(self, items: list[Any]) -> int:
        """Преобразовать числовой токен в целое число."""
        return int(str(items[0]))

    def constant_ref(self, items: list[Any]) -> ConstantReference:
        """Создать ссылку на константу."""
        return ConstantReference(str(items[0]))

    def pair(self, items: list[Any]) -> tuple[str, RawValue]:
        """Создать пару имени и значения словаря."""
        return str(items[0]), items[1]

    def pair_list(
        self,
        items: list[tuple[str, RawValue]],
    ) -> list[tuple[str, RawValue]]:
        """Собрать пары словаря в список."""
        return list(items)

    def dictionary(self, items: list[Any]) -> dict[str, RawValue]:
        """Построить словарь с проверкой повторяющихся имён."""
        pairs = items[0] if items else []
        result: dict[str, RawValue] = {}
        for name, value in pairs:
            if name in result:
                message = f"повторяющееся имя в словаре: {name}"
                raise ConfigLanguageError(message)
            result[name] = value
        return result


def parse_source(source: str) -> list[Declaration]:
    """Разобрать исходный текст и вернуть список объявлений."""
    try:
        tree = LANGUAGE_PARSER.parse(source)
        result = ConfigTransformer().transform(tree)
    except UnexpectedInput as error:
        raise _syntax_error(source, error) from error
    except VisitError as error:
        if isinstance(error.orig_exc, ConfigLanguageError):
            raise error.orig_exc from error
        raise
    return result


def _syntax_error(
    source: str,
    error: UnexpectedInput,
) -> ConfigLanguageError:
    """Создать понятное сообщение о синтаксической ошибке."""
    context = error.get_context(source, span=30).strip()
    message = (
        f"синтаксическая ошибка: строка {error.line}, "
        f"столбец {error.column}: {context}"
    )
    return ConfigLanguageError(message)

