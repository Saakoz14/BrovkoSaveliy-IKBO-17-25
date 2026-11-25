"""Тесты вычисления констант при трансляции."""

import unittest

from src.errors import ConfigLanguageError
from src.parser import parse_source
from src.resolver import resolve_constants


class ResolverTest(unittest.TestCase):
    """Проверка ссылок, ошибок и циклов."""

    def test_resolves_forward_reference(self) -> None:
        """Ссылка может указывать на объявление ниже по тексту."""
        source = "global first = $[second] global second = 42"
        result = resolve_constants(parse_source(source))
        self.assertEqual(result, {"first": 42, "second": 42})

    def test_resolves_dictionary_reference(self) -> None:
        """Ссылка может возвращать целый словарь."""
        source = "global copy = $[original] "
        source += "global original = dict(value = 5)"
        result = resolve_constants(parse_source(source))
        self.assertEqual(result["copy"], {"value": 5})

    def test_rejects_unknown_constant(self) -> None:
        """Неизвестная ссылка создаёт понятную ошибку."""
        declarations = parse_source("global value = $[missing]")
        with self.assertRaisesRegex(ConfigLanguageError, "неизвестная"):
            resolve_constants(declarations)

    def test_rejects_duplicate_global_name(self) -> None:
        """Глобальное имя нельзя объявить дважды."""
        declarations = parse_source("global value = 1 global value = 2")
        with self.assertRaisesRegex(ConfigLanguageError, "повторное"):
            resolve_constants(declarations)

    def test_rejects_reference_cycle(self) -> None:
        """Циклические ссылки выявляются до генерации TOML."""
        source = "global first = $[second] global second = $[first]"
        declarations = parse_source(source)
        with self.assertRaisesRegex(ConfigLanguageError, "циклическая"):
            resolve_constants(declarations)


if __name__ == "__main__":
    unittest.main()

