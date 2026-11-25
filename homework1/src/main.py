"""Точка входа CLI-транслятора учебного языка в TOML."""

from __future__ import annotations

import sys

from .errors import ConfigLanguageError
from .parser import parse_source
from .resolver import resolve_constants
from .toml_writer import to_toml


SUCCESS_CODE = 0
ERROR_CODE = 1


def translate(source: str) -> str:
    """Выполнить полный перевод исходного текста в TOML."""
    declarations = parse_source(source)
    values = resolve_constants(declarations)
    return to_toml(values)


def main() -> int:
    """Прочитать stdin, вывести TOML или сообщение об ошибке."""
    source = sys.stdin.read()
    try:
        result = translate(source)
    except ConfigLanguageError as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return ERROR_CODE
    sys.stdout.write(result)
    return SUCCESS_CODE


if __name__ == "__main__":
    sys.exit(main())

