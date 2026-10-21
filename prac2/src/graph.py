"""Построение транзитивного графа зависимостей.

Файл выполняет BFS без рекурсии, учитывает максимальную глубину и фильтр,
защищается от циклов и формирует текстовый список смежности.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field

from .models import PackageRef
from .repository import DependencyRepository


@dataclass
class DependencyGraph:
    """Ориентированный граф зависимостей пакетов."""

    adjacency: dict[PackageRef, list[PackageRef]] = field(
        default_factory=dict
    )

    def add_node(self, package: PackageRef) -> None:
        """Добавить вершину, если её ещё нет."""
        self.adjacency.setdefault(package, [])

    def add_edge(self, source: PackageRef, target: PackageRef) -> None:
        """Добавить ориентированное ребро без дублирования."""
        self.add_node(source)
        self.add_node(target)
        if target not in self.adjacency[source]:
            self.adjacency[source].append(target)

    def format_lines(self) -> list[str]:
        """Представить граф как отсортированный список смежности."""
        lines: list[str] = []
        for package in sorted(self.adjacency, key=_package_key):
            targets = sorted(self.adjacency[package], key=_package_key)
            labels = ", ".join(target.label() for target in targets)
            lines.append(f"{package.label()} -> {labels or '(нет)'}")
        return lines


def build_graph_bfs(
    repository: DependencyRepository,
    root: PackageRef,
    max_depth: int,
    filter_substring: str,
) -> DependencyGraph:
    """Построить граф очередью BFS без рекурсивных вызовов."""
    graph = DependencyGraph()
    graph.add_node(root)
    queue = deque([(root, 0)])
    expanded: set[PackageRef] = set()
    filtered = filter_substring.casefold()
    while queue:
        package, depth = queue.popleft()
        if package in expanded:
            continue
        expanded.add(package)
        if depth >= max_depth:
            continue
        dependencies = repository.get_direct_dependencies(
            package.name, package.version
        )
        for dependency in dependencies:
            if filtered and filtered in dependency.name.casefold():
                continue
            version = repository.resolve_version(
                dependency.name, dependency.version_spec
            )
            child = PackageRef(dependency.name, version)
            graph.add_edge(package, child)
            if child not in expanded:
                queue.append((child, depth + 1))
    return graph


def _package_key(package: PackageRef) -> tuple[str, str]:
    return package.name.casefold(), package.version

