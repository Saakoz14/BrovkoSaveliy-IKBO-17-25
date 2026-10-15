"""Виртуальная файловая система в памяти."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


class VfsError(Exception):
    """Ошибка загрузки VFS."""


@dataclass
class VfsNode:
    """Каталог или файл VFS."""

    name: str
    is_directory: bool
    content: bytes | None = None
    children: dict[str, "VfsNode"] = field(default_factory=dict)


@dataclass
class VirtualFileSystem:
    """Копия дерева каталогов в памяти."""

    name: str
    root: VfsNode

    @classmethod
    def from_directory(cls, source: Path) -> "VirtualFileSystem":
        """Рекурсивно прочитать директорию."""
        path = source.expanduser()
        if not path.exists():
            raise VfsError(f"директория не найдена: {path}")
        if not path.is_dir():
            message = f"путь не является директорией: {path}"
            raise VfsError(message)
        try:
            root = cls._read_directory(path, path.name or "/")
        except OSError as error:
            message = f"не удалось прочитать {path}: {error}"
            raise VfsError(message) from error
        return cls(name=path.name or "/", root=root)

    @classmethod
    def _read_directory(cls, path: Path, name: str) -> VfsNode:
        node = VfsNode(name=name, is_directory=True)
        for child_path in sorted(path.iterdir(), key=lambda item: item.name):
            if child_path.is_symlink():
                message = (
                    "символические ссылки не поддерживаются: "
                    f"{child_path}"
                )
                raise VfsError(message)
            if child_path.is_dir():
                child = cls._read_directory(child_path, child_path.name)
            elif child_path.is_file():
                child = VfsNode(
                    name=child_path.name,
                    is_directory=False,
                    content=child_path.read_bytes(),
                )
            else:
                message = f"неподдерживаемый объект: {child_path}"
                raise VfsError(message)
            node.children[child.name] = child
        return node

    @property
    def file_count(self) -> int:
        """Вернуть количество файлов в памяти."""
        return self._count_nodes(self.root)[0]

    @property
    def directory_count(self) -> int:
        """Посчитать каталоги, включая корневой."""
        return self._count_nodes(self.root)[1]

    @property
    def total_size(self) -> int:
        """Посчитать размер файлов."""
        return self._count_nodes(self.root)[2]

    @classmethod
    def _count_nodes(cls, node: VfsNode) -> tuple[int, int, int]:
        if not node.is_directory:
            return 1, 0, len(node.content or b"")
        files, directories, size = 0, 1, 0
        for child in node.children.values():
            counts = cls._count_nodes(child)
            child_files, child_directories, child_size = counts
            files += child_files
            directories += child_directories
            size += child_size
        return files, directories, size

    def find(self, path: str) -> VfsNode:
        """Найти узел по пути внутри VFS."""
        node = self.root
        for part in (item for item in path.split("/") if item):
            if not node.is_directory or part not in node.children:
                message = f"путь внутри VFS не найден: {path}"
                raise VfsError(message)
            node = node.children[part]
        return node
