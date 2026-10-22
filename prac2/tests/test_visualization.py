"""Тесты создания SVG-изображения графа."""

import tempfile
import unittest
from pathlib import Path

from src.graph import DependencyGraph
from src.models import PackageRef
from src.visualization import save_graph_svg


class VisualizationTest(unittest.TestCase):
    """Проверка сохранения блоков и стрелок в SVG."""

    def test_saves_graph_as_svg(self) -> None:
        root = PackageRef("A", "1.0.0")
        child = PackageRef("B", "1.0.0")
        graph = DependencyGraph()
        graph.add_edge(root, child)

        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "graph.svg"
            result = save_graph_svg(graph, root, output)
            content = result.read_text(encoding="utf-8")

        self.assertEqual(result, output)
        self.assertIn("A@1.0.0", content)
        self.assertIn("B@1.0.0", content)
        self.assertIn('marker-end="url(#arrow)"', content)


if __name__ == "__main__":
    unittest.main()
