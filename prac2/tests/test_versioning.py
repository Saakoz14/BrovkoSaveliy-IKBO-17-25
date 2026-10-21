"""Тесты выбора версий NuGet."""

import unittest

from src.versioning import VersionError, select_version


class VersioningTest(unittest.TestCase):
    """Проверка основных форм диапазонов NuGet."""

    def setUp(self) -> None:
        self.versions = [
            "1.0.0",
            "1.5.0",
            "2.0.0-beta.1",
            "2.0.0",
            "3.0.0",
        ]

    def test_selects_exact_version(self) -> None:
        result = select_version(self.versions, "[1.0]")
        self.assertEqual(result, "1.0.0")

    def test_selects_highest_version_in_range(self) -> None:
        result = select_version(self.versions, "[1.0.0,2.0.0)")
        self.assertEqual(result, "1.5.0")

    def test_bare_version_is_inclusive_minimum(self) -> None:
        result = select_version(self.versions, "2.0.0")
        self.assertEqual(result, "3.0.0")

    def test_rejects_empty_range(self) -> None:
        with self.assertRaisesRegex(VersionError, "нет версии"):
            select_version(self.versions, "[4.0.0,5.0.0)")


if __name__ == "__main__":
    unittest.main()

