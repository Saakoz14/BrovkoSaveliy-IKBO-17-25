"""Создание изображения графа зависимостей в формате SVG.

Файл располагает пакеты по уровням, рисует между ними стрелки и сохраняет
готовую схему без использования сторонних библиотек.
"""

from __future__ import annotations

from collections import deque
from html import escape
from pathlib import Path

from .graph import DependencyGraph
from .models import PackageRef


NODE_WIDTH = 180
NODE_HEIGHT = 54
HORIZONTAL_GAP = 100
VERTICAL_GAP = 32
MARGIN = 50


def save_graph_svg(
    graph: DependencyGraph,
    root: PackageRef,
    output_path: Path,
) -> Path:
    """Сохранить граф в виде изображения SVG и вернуть путь к нему."""
    levels = _calculate_levels(graph, root)
    columns = _group_by_level(levels)
    positions = _calculate_positions(columns)
    width = _canvas_width(columns)
    height = _canvas_height(columns)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        _build_svg(graph, positions, width, height),
        encoding="utf-8",
    )
    return output_path


def _calculate_levels(
    graph: DependencyGraph,
    root: PackageRef,
) -> dict[PackageRef, int]:
    """Определить минимальный уровень каждой вершины обходом BFS."""
    levels = {root: 0}
    queue = deque([root])
    while queue:
        package = queue.popleft()
        for child in graph.adjacency.get(package, []):
            if child in levels:
                continue
            levels[child] = levels[package] + 1
            queue.append(child)

    last_level = max(levels.values(), default=-1) + 1
    for package in graph.adjacency:
        levels.setdefault(package, last_level)
    return levels


def _group_by_level(
    levels: dict[PackageRef, int],
) -> dict[int, list[PackageRef]]:
    """Собрать вершины в колонки по глубине графа."""
    columns: dict[int, list[PackageRef]] = {}
    for package, level in levels.items():
        columns.setdefault(level, []).append(package)
    for packages in columns.values():
        packages.sort(key=lambda package: package.label().casefold())
    return columns


def _calculate_positions(
    columns: dict[int, list[PackageRef]],
) -> dict[PackageRef, tuple[float, float]]:
    """Вычислить координаты левого верхнего угла каждого блока."""
    positions: dict[PackageRef, tuple[float, float]] = {}
    largest_column = max((len(items) for items in columns.values()), default=1)
    content_height = (
        largest_column * NODE_HEIGHT
        + max(largest_column - 1, 0) * VERTICAL_GAP
    )
    for level, packages in columns.items():
        column_height = (
            len(packages) * NODE_HEIGHT
            + max(len(packages) - 1, 0) * VERTICAL_GAP
        )
        start_y = MARGIN + (content_height - column_height) / 2
        x = MARGIN + level * (NODE_WIDTH + HORIZONTAL_GAP)
        for index, package in enumerate(packages):
            y = start_y + index * (NODE_HEIGHT + VERTICAL_GAP)
            positions[package] = (x, y)
    return positions


def _canvas_width(columns: dict[int, list[PackageRef]]) -> int:
    level_count = max(columns, default=0) + 1
    return (
        2 * MARGIN
        + level_count * NODE_WIDTH
        + max(level_count - 1, 0) * HORIZONTAL_GAP
    )


def _canvas_height(columns: dict[int, list[PackageRef]]) -> int:
    largest_column = max((len(items) for items in columns.values()), default=1)
    return (
        2 * MARGIN
        + largest_column * NODE_HEIGHT
        + max(largest_column - 1, 0) * VERTICAL_GAP
    )


def _build_svg(
    graph: DependencyGraph,
    positions: dict[PackageRef, tuple[float, float]],
    width: int,
    height: int,
) -> str:
    """Сформировать XML-разметку SVG с линиями и блоками."""
    parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        (
            f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'width="{width}" height="{height}" '
            f'viewBox="0 0 {width} {height}">'
        ),
        "<defs>",
        (
            '<marker id="arrow" markerWidth="10" markerHeight="10" '
            'refX="9" refY="3" orient="auto" markerUnits="strokeWidth">'
        ),
        '<path d="M0,0 L0,6 L9,3 z" fill="#9da5b4"/>',
        "</marker>",
        "</defs>",
        f'<rect width="{width}" height="{height}" fill="#1e1f22"/>',
    ]

    for source, targets in graph.adjacency.items():
        source_x, source_y = positions[source]
        for target in targets:
            target_x, target_y = positions[target]
            parts.append(
                _edge_svg(source_x, source_y, target_x, target_y)
            )

    for package, (x, y) in positions.items():
        parts.extend(_node_svg(package, x, y))

    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def _edge_svg(
    source_x: float,
    source_y: float,
    target_x: float,
    target_y: float,
) -> str:
    """Нарисовать стрелку между центрами границ двух блоков."""
    if target_x > source_x:
        start_x = source_x + NODE_WIDTH
        end_x = target_x
    else:
        start_x = source_x
        end_x = target_x + NODE_WIDTH
    start_y = source_y + NODE_HEIGHT / 2
    end_y = target_y + NODE_HEIGHT / 2
    return (
        f'<line x1="{start_x}" y1="{start_y}" '
        f'x2="{end_x}" y2="{end_y}" '
        'stroke="#9da5b4" stroke-width="2" marker-end="url(#arrow)"/>'
    )


def _node_svg(
    package: PackageRef,
    x: float,
    y: float,
) -> list[str]:
    """Нарисовать блок пакета и подпись внутри него."""
    text_x = x + NODE_WIDTH / 2
    text_y = y + NODE_HEIGHT / 2 + 5
    label = escape(package.label())
    return [
        (
            f'<rect x="{x}" y="{y}" width="{NODE_WIDTH}" '
            f'height="{NODE_HEIGHT}" rx="10" fill="#2b2d30" '
            'stroke="#5794f2" stroke-width="2"/>'
        ),
        (
            f'<text x="{text_x}" y="{text_y}" text-anchor="middle" '
            'font-family="Arial, sans-serif" font-size="16" '
            f'fill="#f2f2f2">{label}</text>'
        ),
    ]
