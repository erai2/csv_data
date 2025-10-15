"""Visualisation helpers for relation networks."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, Tuple

from pyvis.network import Network


def draw_relation_network(name: str, relations: Iterable[Tuple[str, str, str]]) -> Path:
    """Render relations into an interactive HTML network graph."""

    net = Network(height="650px", width="100%", directed=False, bgcolor="#111", font_color="#eee")
    net.barnes_hut()

    for source, target, relation in relations:
        source = source.strip()
        target = target.strip()
        rel = relation.strip()

        if not source or not target:
            continue

        color = _relation_color(rel)
        net.add_node(source, label=source, color="#2c7be5")
        net.add_node(target, label=target, color="#f6c23e")
        net.add_edge(source, target, label=rel, color=color)

    output_dir = Path("data/uploads")
    output_dir.mkdir(parents=True, exist_ok=True)
    html_path = output_dir / f"{name or 'relation'}_network.html"
    net.save_graph(str(html_path))
    return html_path


def _relation_color(relation: str) -> str:
    mapping = {
        "合": "#28a745",
        "沖": "#d9534f",
        "破": "#fd7e14",
        "刑": "#6c757d",
        "害": "#6610f2",
    }
    for key, value in mapping.items():
        if key in relation:
            return value
    return "#17a2b8"

