"""Тесты синтаксического анализатора Lark."""

import unittest

from src.errors import ConfigLanguageError
from src.models import ConstantReference
from src.parser import parse_source


class ParserTest(unittest.TestCase):
    """Проверка всех синтаксических конструкций языка."""

    def test_parses_numbers_comments_and_nested_dictionaries(self) -> None:
        """Парсер принимает числа, комментарии и вложенность."""
        source = """
        %{ comment %}
        global config = dict(
            positive = +12,
            negative = -7,
            nested = dict(value = 3),
        )
        """
        value = parse_source(source)[0].value
        self.assertEqual(value["positive"], 12)
        self.assertEqual(value["negative"], -7)
        self.assertEqual(value["nested"], {"value": 3})

    def test_parses_constant_reference(self) -> None:
        """Парсер создаёт объект ссылки на константу."""
        declaration = parse_source("global result = $[source]")[0]
        self.assertEqual(
            declaration.value,
            ConstantReference("source"),
        )

    def test_rejects_invalid_name(self) -> None:
        """Имя с заглавной буквы считается ошибкой."""
        with self.assertRaisesRegex(ConfigLanguageError, "строка"):
            parse_source("global Invalid = 1")

    def test_rejects_missing_comma(self) -> None:
        """Между элементами словаря обязательна запятая."""
        source = "global item = dict(first = 1 second = 2)"
        with self.assertRaisesRegex(ConfigLanguageError, "столбец"):
            parse_source(source)

    def test_rejects_duplicate_dictionary_key(self) -> None:
        """Повторное имя внутри словаря запрещено."""
        source = "global item = dict(value = 1, value = 2)"
        with self.assertRaisesRegex(ConfigLanguageError, "повторяющееся"):
            parse_source(source)


if __name__ == "__main__":
    unittest.main()

