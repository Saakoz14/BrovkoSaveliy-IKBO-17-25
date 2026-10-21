"""Тесты CSV-конфигурации."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src.config import ConfigError, load_config


class ConfigTest(unittest.TestCase):
    """Проверка всех параметров конфигурации."""

    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.directory = Path(self.temporary.name)
        self.repository = self.directory / "repository.csv"
        self.repository.write_text("package,version\nA,1.0.0\n")

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def write_config(self, replacements: dict[str, str] | None = None) -> Path:
        values = {
            "package_name": "A",
            "repository": "repository.csv",
            "test_mode": "true",
            "package_version": "1.0.0",
            "max_depth": "3",
            "filter_substring": "X",
        }
        values.update(replacements or {})
        lines = ["key,value"]
        lines.extend(f"{key},{value}" for key, value in values.items())
        path = self.directory / "config.csv"
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return path

    def test_reads_valid_configuration(self) -> None:
        config = load_config(self.write_config())
        self.assertEqual(config.package_name, "A")
        self.assertEqual(config.max_depth, 3)
        self.assertTrue(config.test_mode)
        self.assertEqual(config.repository, str(self.repository.resolve()))

    def test_rejects_invalid_package_name(self) -> None:
        path = self.write_config({"package_name": "bad package"})
        with self.assertRaisesRegex(ConfigError, "имя пакета"):
            load_config(path)

    def test_rejects_missing_repository(self) -> None:
        path = self.write_config({"repository": "missing.csv"})
        with self.assertRaisesRegex(ConfigError, "не найден"):
            load_config(path)

    def test_rejects_invalid_test_mode(self) -> None:
        path = self.write_config({"test_mode": "yes"})
        with self.assertRaisesRegex(ConfigError, "true или false"):
            load_config(path)

    def test_rejects_invalid_version(self) -> None:
        path = self.write_config({"package_version": "latest"})
        with self.assertRaisesRegex(ConfigError, "версия пакета"):
            load_config(path)

    def test_rejects_negative_depth(self) -> None:
        path = self.write_config({"max_depth": "-1"})
        with self.assertRaisesRegex(ConfigError, "отрицательным"):
            load_config(path)

    def test_rejects_missing_filter_parameter(self) -> None:
        path = self.write_config()
        text = path.read_text(encoding="utf-8")
        text = "\n".join(
            line for line in text.splitlines()
            if not line.startswith("filter_substring,")
        )
        path.write_text(text + "\n", encoding="utf-8")
        with self.assertRaisesRegex(ConfigError, "filter_substring"):
            load_config(path)

    def test_accepts_real_repository_url(self) -> None:
        path = self.write_config(
            {
                "repository": "https://api.nuget.org/v3-flatcontainer",
                "test_mode": "false",
            }
        )
        config = load_config(path)
        self.assertFalse(config.test_mode)


if __name__ == "__main__":
    unittest.main()

