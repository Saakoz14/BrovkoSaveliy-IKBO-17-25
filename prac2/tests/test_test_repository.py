"""Тесты файлового тестового репозитория."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src.models import Dependency
from src.test_repository import TestRepository, TestRepositoryError


class TestRepositoryTest(unittest.TestCase):
    """Проверка чтения тестового CSV-графа."""

    def write_repository(self, rows: str) -> Path:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        path = Path(temporary.name) / "repository.csv"
        header = "package,version,dependency,dependency_version\n"
        path.write_text(header + rows, encoding="utf-8")
        return path

    def test_reads_dependencies(self) -> None:
        path = self.write_repository(
            "A,1.0.0,B,[1.0.0]\nB,1.0.0,,\n"
        )
        repository = TestRepository(path)
        dependencies = repository.get_direct_dependencies("A", "1.0.0")
        self.assertEqual(dependencies, [Dependency("B", "[1.0.0]")])

    def test_rejects_lowercase_package(self) -> None:
        path = self.write_repository("bad,1.0.0,,\n")
        with self.assertRaisesRegex(TestRepositoryError, "A-Z"):
            TestRepository(path)

    def test_rejects_unknown_dependency(self) -> None:
        path = self.write_repository("A,1.0.0,B,[1.0.0]\n")
        with self.assertRaisesRegex(TestRepositoryError, "не описан"):
            TestRepository(path)


if __name__ == "__main__":
    unittest.main()

