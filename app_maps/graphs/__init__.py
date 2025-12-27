import networkx as nx


def demo_shortest_path() -> str:
    """Show a tiny weighted shortest-path example."""
    g = nx.Graph()
    g.add_weighted_edges_from(
        [
            ("A", "B", 1),
            ("B", "C", 2),
            ("A", "C", 4),
            ("C", "D", 1),
        ]
    )
    path = nx.shortest_path(g, "A", "D", weight="weight")
    length = nx.shortest_path_length(g, "A", "D", weight="weight")
    formatted_path = " -> ".join(path)
    return f"Shortest path A->D: {formatted_path} (cost={length})"
