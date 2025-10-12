import os
from typing import Iterable, Tuple

from pyvis.network import Network

Relation = Tuple[str, str, str]


def draw_chart_relations(name: str, relations: Iterable[Relation]) -> str:
    net = Network(height="600px", width="100%", directed=False)

    for start, end, relation in relations:
        color = {
            "合": "green",
            "沖": "red",
            "破": "orange",
            "刑": "gray",
            "墓": "purple",
        }.get(relation, "blue")

        net.add_node(start, label=start)
        net.add_node(end, label=end)
        net.add_edge(start, end, label=relation, color=color)

    output_dir = os.path.join("data", "uploads")
    os.makedirs(output_dir, exist_ok=True)

    html_path = os.path.join(output_dir, f"{name}_relations.html")
    net.save_graph(html_path)
    return html_path
