import pytest
import networkx as nx
from datetime import datetime
from coloring import greedy_coloring, welsh_powell_coloring, dsatur_coloring, backtracking_coloring
from api import generate_synthetic_contests, build_conflict_graph
from scheduler import prioritize_contests, reorder_slots_by_priority

def create_test_graph():
    """Create a cycle graph with 5 nodes for testing."""
    G = nx.cycle_graph(5)
    for node in G.nodes():
        G.nodes[node]['color'] = None
        G.nodes[node]['name'] = f"Contest {node}"
        G.nodes[node]['start_time'] = 0
        G.nodes[node]['duration'] = 3600
        G.nodes[node]['priority'] = 0.5
    return G

@pytest.mark.parametrize("coloring_func", [
    greedy_coloring,
    welsh_powell_coloring,
    dsatur_coloring,
    backtracking_coloring
])
def test_coloring_validity(coloring_func):
    """Test that no adjacent nodes share the same color."""
    G = create_test_graph()
    coloring_func(G)
    for u, v in G.edges():
        assert G.nodes[u]['color'] != G.nodes[v]['color'], f"{coloring_func.__name__} failed: adjacent nodes have same color"

def test_backtracking_optimal():
    """Test that backtracking finds the optimal number of colors."""
    G = create_test_graph()
    backtracking_coloring(G)
    colors = len(set(G.nodes[node]['color'] for node in G.nodes()))
    assert colors <= 3, "Backtracking used more colors than necessary for a cycle graph"

def test_synthetic_contests_time_window():
    """Test synthetic contest generation within time window."""
    base_time = int(datetime.now().timestamp())
    time_window = 3 * 24 * 3600  # 3 days
    contests = generate_synthetic_contests(5, base_time, time_window)
    assert len(contests) == 5, "Incorrect number of synthetic contests"
    for _, data in contests:
        assert base_time <= data['start_time'] <= base_time + time_window, "Contest outside time window"
        assert 'name' in data and 'Synthetic' in data['name'], "Invalid contest name"

def test_priority_reordering():
    """Test that slots are reordered by priority."""
    G = create_test_graph()
    G.nodes[0]['priority'] = 1.5  # High priority
    G.nodes[1]['priority'] = 0.5
    dsatur_coloring(G)
    reorder_slots_by_priority(G)
    high_priority_slot = G.nodes[0]['color']
    assert high_priority_slot == 0, "High-priority contest not in earliest slot"