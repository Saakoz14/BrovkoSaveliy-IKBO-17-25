"""Тесты загрузки VFS."""

import tempfile
import unittest
from pathlib import Path

from src.vfs import VfsError, VirtualFileSystem


class VirtualFileSystemTest(unittest.TestCase):
    """Проверка копирования каталогов в память."""

    def test_loads_nested_directory_and_file_contents(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "vfs"
            nested = source / "one" / "two" / "three"
            nested.mkdir(parents=True)
            (nested / "data.txt").write_bytes(b"content")
            vfs = VirtualFileSystem.from_directory(source)
        node = vfs.find("/one/two/three/data.txt")
        self.assertFalse(node.is_directory)
        self.assertEqual(node.content, b"content")
        self.assertEqual(vfs.file_count, 1)
        self.assertEqual(vfs.directory_count, 4)

    def test_data_remains_available_after_source_is_removed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "vfs"
            source.mkdir()
            file_path = source / "hello.txt"
            file_path.write_text("hello", encoding="utf-8")
            vfs = VirtualFileSystem.from_directory(source)
        self.assertEqual(vfs.find("hello.txt").content, b"hello")

    def test_missing_directory_is_an_error(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            missing = Path(directory) / "missing"
            with self.assertRaisesRegex(VfsError, "не найдена"):
                VirtualFileSystem.from_directory(missing)

    def test_regular_file_cannot_be_vfs_source(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "file.txt"
            source.write_text("data", encoding="utf-8")
            error = "не является директорией"
            with self.assertRaisesRegex(VfsError, error):
                VirtualFileSystem.from_directory(source)


if __name__ == "__main__":
    unittest.main()
