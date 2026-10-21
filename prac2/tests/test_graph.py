"""Тесты BFS-графа зависимостей."""

import unittest

from src.graph import build_graph_bfs
from src.models import Dependency, PackageRef


class FakeRepository:
    """Источник зависимостей для модульных тестов."""

    def __init__(self, mapping: dict[str, list[str]]) -> None:
        self.mapping = mapping

    def get_direct_dependencies(
        self, package_name: str, package_version: str
    ) -> list[Dependency]:
        del package_version
        return [
            Dependency(name, "[1.0.0]")
            for name in self.mapping.get(package_name, [])
        ]

    def resolve_version(self, package_name: str, version_spec: str) -> str:
        del package_name, version_spec
        return "1.0.0"


class DependencyGraphTest(unittest.TestCase):
    """Проверка транзитивности, глубины, фильтра и циклов."""

    def build(
        self,
        mapping: dict[str, list[str]],
        depth: int = 10,
        filtered: str = "",
    ):
        repository = FakeRepository(mapping)
        return build_graph_bfs(
            repository,
            PackageRef("A", "1.0.0"),
            depth,
            filtered,
        )

    def test_builds_transitive_graph(self) -> None:
        graph = self.build({"A": ["B"], "B": ["C"], "C": []})
        labels = {package.label() for package in graph.adjacency}
        self.assertEqual(labels, {"A@1.0.0", "B@1.0.0", "C@1.0.0"})

    def test_respects_maximum_depth(self) -> None:
        graph = self.build(
            {"A": ["B"], "B": ["C"], "C": ["D"]},
            depth=1,
        )
        labels = {package.name for package in graph.adjacency}
        self.assertEqual(labels, {"A", "B"})

    def test_filters_package_and_its_branch(self) -> None:
        graph = self.build(
            {"A": ["B", "SKIP"], "SKIP": ["C"]},
            filtered="skip",
        )
        labels = {package.name for package in graph.adjacency}
        self.assertEqual(labels, {"A", "B"})

    def test_handles_cycle(self) -> None:
        graph = self.build({"A": ["B"], "B": ["C"], "C": ["A"]})
        self.assertEqual(len(graph.adjacency), 3)
        node_c = PackageRef("C", "1.0.0")
        self.assertIn(PackageRef("A", "1.0.0"), graph.adjacency[node_c])


if __name__ == "__main__":
    unittest.main()

