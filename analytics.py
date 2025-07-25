import networkx as nx
import matplotlib.pyplot as plt
from matplotlib import colors as mcolors
from coloring import greedy_coloring, welsh_powell_coloring, dsatur_coloring, backtracking_coloring
import time
import copy
from datetime import datetime, timedelta

def compare_algorithms(G):
    """Compare coloring algorithms by number of colors and execution time."""
    algorithms = [
        ('Greedy', greedy_coloring),
        ('Welsh-Powell', welsh_powell_coloring),
        ('DSatur', dsatur_coloring),
        ('Backtracking', backtracking_coloring)
    ]
    results = []
    for name, func in algorithms:
        G_copy = copy.deepcopy(G)
        start_time = time.time()
        func(G_copy)
        time_taken = time.time() - start_time
        colors = len(set(data['color'] for _, data in G_copy.nodes(data=True)))
        results.append((name, colors, time_taken))
    return results

def compute_analytics(G, days):
    """Compute analytics: graph density, contests per slot, average priority."""
    n = G.number_of_nodes()
    e = G.number_of_edges()
    max_edges = n * (n - 1) / 2
    density = e / max_edges if max_edges > 0 else 0
    num_colors = len(set(data['color'] for _, data in G.nodes(data=True)))
    contests_per_slot = n / num_colors if num_colors > 0 else 0
    total_priority = sum(data['priority'] for _, data in G.nodes(data=True))
    avg_priority_per_slot = total_priority / num_colors if num_colors > 0 else 0
    return {
        'density': density,
        'avg_contests_per_slot': contests_per_slot,
        'avg_priority_per_slot': avg_priority_per_slot
    }

def plot_conflict_graph(G, filename):
    """Plot the conflict graph with nodes colored by slot."""
    plt.figure(figsize=(10, 8))
    pos = nx.spring_layout(G, seed=42)
    num_colors = len(set(data['color'] for _, data in G.nodes(data=True)))
    cmap = plt.cm.get_cmap('tab20', max(1, num_colors))
    node_colors = [data['color'] for _, data in G.nodes(data=True)]
    nx.draw(G, pos, node_color=node_colors, cmap=cmap, with_labels=False, node_size=500, edge_color='gray')
    labels = {node: data['name'][:10] + '...' if len(data['name']) > 10 else data['name'] for node, data in G.nodes(data=True)}
    nx.draw_networkx_labels(G, pos, labels, font_size=8)
    plt.title("Conflict Graph: Nodes Colored by Slot")
    plt.savefig(filename, bbox_inches='tight')
    plt.close()

def plot_algorithm_comparison(comparison, filename):
    """Plot a bar chart comparing algorithm performance."""
    algorithms = [alg for alg, _, _ in comparison]
    colors = [colors for _, colors, _ in comparison]
    times = [time_taken for _, _, time_taken in comparison]
    
    fig, ax1 = plt.subplots(figsize=(10, 6))
    
    x = range(len(algorithms))
    width = 0.35
    ax1.bar([i - width/2 for i in x], colors, width, label='Number of Colors', color='skyblue')
    ax1.set_xlabel('Algorithm')
    ax1.set_ylabel('Number of Colors', color='skyblue')
    ax1.set_xticks(x)
    ax1.set_xticklabels(algorithms)
    ax1.tick_params(axis='y', labelcolor='skyblue')
    
    ax2 = ax1.twinx()
    ax2.bar([i + width/2 for i in x], times, width, label='Execution Time (s)', color='salmon')
    ax2.set_ylabel('Execution Time (s)', color='salmon')
    ax2.tick_params(axis='y', labelcolor='salmon')
    
    fig.suptitle('Algorithm Performance Comparison')
    fig.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=2)
    plt.savefig(filename, bbox_inches='tight')
    plt.close()

def plot_gantt_chart(G, days, filename):
    """Plot a Gantt chart of the schedule by day and slot."""
    fig, ax = plt.subplots(figsize=(12, 8))
    y_pos = []
    widths = []
    starts = []
    labels = []
    colors = []
    cmap = plt.cm.get_cmap('tab20', len(set(data['color'] for _, data in G.nodes(data=True))))
    
    y = 0
    for i, day_slots in enumerate(days):
        for slot in day_slots:
            for node, data in G.nodes(data=True):
                if data['color'] == slot:
                    start_time = datetime.fromtimestamp(data['start_time'])
                    duration = data['duration'] / 3600  # Convert to hours
                    base_time = datetime.fromtimestamp(min(data['start_time'] for _, data in G.nodes(data=True)))
                    start_offset = (start_time - base_time).total_seconds() / 3600  # Hours since earliest start
                    y_pos.append(y)
                    starts.append(start_offset)
                    widths.append(duration)
                    labels.append(data['name'][:15] + '...' if len(data['name']) > 15 else data['name'])
                    colors.append(cmap(slot))
            y += 1
    
    ax.barh(y_pos, widths, left=starts, color=colors, edgecolor='black')
    ax.set_yticks(range(y))
    ax.set_yticklabels([f"Day {i//3 + 1} Slot {(i%3) + 1}" for i in range(y)])
    ax.set_xlabel('Time (Hours from Earliest Start)')
    ax.set_title('Contest Schedule Gantt Chart')
    for i, label in enumerate(labels):
        ax.text(starts[i] + widths[i]/2, y_pos[i], label, ha='center', va='center', fontsize=8, color='white')
    plt.savefig(filename, bbox_inches='tight')
    plt.close()