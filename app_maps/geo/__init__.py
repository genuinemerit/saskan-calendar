from math import hypot


def demo_distance() -> str:
    """Compute a simple Euclidean distance demo."""
    a = (0, 0)
    b = (3, 4)
    dist = hypot(b[0] - a[0], b[1] - a[1])
    return f"Distance from {a} to {b}: {dist:.2f}"
