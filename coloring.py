import networkx as nx
import heapq
import time

def mex(colors):
    """Find the smallest non-negative integer not in the set."""
    m = 0
    while m in colors:
        m += 1
    return m

def greedy_coloring(g, nodes=None):
    """Greedy coloring algorithm."""
    nodes = nodes or list(g.nodes())
    for node in nodes:
        used_colors = [g.nodes[neighbor]['color'] for neighbor in g.neighbors(node) if g.nodes[neighbor]['color'] is not None]
        g.nodes[node]['color'] = mex(set(used_colors))

def welsh_powell_coloring(g, nodes=None):
    """Welsh-Powell coloring: prioritize high-degree nodes."""
    nodes = nodes or sorted(g.nodes(), key=lambda x: g.degree(x), reverse=True)
    for node in nodes:
        used_colors = [g.nodes[neighbor]['color'] for neighbor in g.neighbors(node) if g.nodes[neighbor]['color'] is not None]
        g.nodes[node]['color'] = mex(set(used_colors))

def dsatur_coloring(g, nodes=None):
    """DSatur coloring: prioritize nodes with highest saturation degree and priority."""
    if not nodes:
        nodes = list(g.nodes())
        saturation = {node: 0 for node in nodes}
        colored = set()
        # Prioritize by degree and priority
        degrees = [(-g.degree(node) - g.nodes[node].get('priority', 0), node) for node in nodes]
        heapq.heapify(degrees)
    else:
        saturation = {node: len(set(g.nodes[n]['color'] for n in g.neighbors(node) if g.nodes[n]['color'] is not None)) for node in nodes}
        colored = set(g.nodes()) - set(nodes)
        degrees = [(-saturation[node] - g.nodes[node].get('priority', 0), node) for node in nodes]
        heapq.heapify(degrees)

    while degrees:
        _, node = heapq.heappop(degrees)
        if node not in colored:
            used_colors = [g.nodes[neighbor]['color'] for neighbor in g.neighbors(node) if g.nodes[neighbor]['color'] is not None]
            g.nodes[node]['color'] = mex(set(used_colors))
            colored.add(node)
            for neighbor in g.neighbors(node):
                if neighbor not in colored:
                    saturation[neighbor] = len(set(g.nodes[n]['color'] for n in g.neighbors(neighbor) if g.nodes[n]['color'] is not None))
                    heapq.heappush(degrees, (-saturation[neighbor] - g.nodes[neighbor].get('priority', 0), neighbor))

def backtracking_coloring(g, nodes=None):
    """Optimized backtracking for optimal coloring."""
    def can_color(node, color, g, colors):
        return all(g.nodes[neighbor]['color'] != color for neighbor in g.neighbors(node))

    def backtrack(nodes, colors, g, max_colors, current=0):
        if current == len(nodes):
            return True
        node = nodes[current]
        for c in range(max_colors):
            if can_color(node, c, g, colors):
                g.nodes[node]['color'] = c
                if backtrack(nodes, colors, g, max_colors, current + 1):
                    return True
                g.nodes[node]['color'] = None
        return False

    nodes = nodes or sorted(g.nodes(), key=lambda x: g.degree(x) + g.nodes[x].get('priority', 0), reverse=True)
    max_colors = max(1, max((g.degree(node) for node in g.nodes()), default=0)) + 1
    while max_colors > 1:
        for node in g.nodes():
            g.nodes[node]['color'] = None
        if backtrack(nodes, {}, g, max_colors):
            break
        max_colors += 1