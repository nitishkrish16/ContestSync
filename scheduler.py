import argparse
import json
import networkx as nx
from datetime import datetime, timedelta
import random
from coloring import greedy_coloring, welsh_powell_coloring, dsatur_coloring, backtracking_coloring
from api import fetch_contests, build_conflict_graph, generate_synthetic_contests
from analytics import compare_algorithms, compute_analytics, plot_conflict_graph, plot_algorithm_comparison, plot_gantt_chart

def prioritize_contests(contests):
    """Assign priorities based on platform and duration."""
    platform_priority = {'Codeforces': 1.0, 'LeetCode': 0.8, 'HackerRank': 0.7, 'Synthetic': 0.6}
    for contest_id, data in contests:
        platform = data['name'].split()[0] if data['name'].split() else 'Unknown'
        data['priority'] = platform_priority.get(platform, 0.5) * (1 + 1 / (data['duration'] / 3600))
    return sorted(contests, key=lambda x: x[1]['priority'], reverse=True)

def assign_slots_to_days(G, max_slots_per_day=3):
    """Assign slots to days to minimize total duration."""
    num_colors = len(set(data['color'] for _, data in G.nodes(data=True)))
    days = []
    current_day = []
    for slot in range(num_colors):
        if len(current_day) < max_slots_per_day:
            current_day.append(slot)
        else:
            days.append(current_day)
            current_day = [slot]
    if current_day:
        days.append(current_day)
    return days

def reorder_slots_by_priority(G):
    """Reorder slots so high-priority contests are in earlier slots."""
    slot_priority = {}
    num_colors = len(set(data['color'] for _, data in G.nodes(data=True)))
    for slot in range(num_colors):
        total_priority = sum(data['priority'] for node, data in G.nodes(data=True) if data['color'] == slot)
        count = sum(1 for node, data in G.nodes(data=True) if data['color'] == slot)
        slot_priority[slot] = total_priority / count if count > 0 else 0
    slot_mapping = {old: new for new, (old, _) in enumerate(sorted(slot_priority.items(), key=lambda x: x[1], reverse=True))}
    for node, data in G.nodes(data=True):
        data['color'] = slot_mapping[data['color']]

def save_schedule(G, days, filename="output/schedule.json"):
    """Export schedule as JSON with day assignments."""
    schedule = {f"Day {i+1}": [] for i in range(len(days))}
    for i, day_slots in enumerate(days):
        for slot in day_slots:
            for node, data in G.nodes(data=True):
                if data['color'] == slot:
                    schedule[f"Day {i+1}"].append({
                        'name': data['name'],
                        'start_time': datetime.fromtimestamp(data['start_time']).isoformat(),
                        'duration': data['duration'] // 60,
                        'priority': data['priority'],
                        'original_slot': slot + 1
                    })
    with open(filename, 'w') as f:
        json.dump(schedule, f, indent=2)
    print(f"Schedule saved to {filename}")

def add_contest(G, new_contest, algorithm='dsatur'):
    """Dynamically add a new contest to the graph."""
    G.add_node(new_contest[0], **new_contest[1])
    for node, data in G.nodes(data=True):
        if node != new_contest[0]:
            start1, end1 = new_contest[1]['start_time'], new_contest[1]['start_time'] + new_contest[1]['duration']
            start2, end2 = data['start_time'], data['start_time'] + data['duration']
            if not (end1 <= start2 or end2 <= start1):
                G.add_edge(new_contest[0], node)
    if algorithm == 'greedy':
        greedy_coloring(G, nodes=[new_contest[0]])
    elif algorithm == 'welsh_powell':
        welsh_powell_coloring(G, nodes=[new_contest[0]])
    elif algorithm == 'dsatur':
        dsatur_coloring(G, nodes=[new_contest[0]])
    elif algorithm == 'backtracking':
        backtracking_coloring(G, nodes=[new_contest[0]])

def main():
    parser = argparse.ArgumentParser(description="Contest Scheduler: Optimizes contest schedules with time-window constraints and visualizations.")
    parser.add_argument('--num_contests', type=int, default=10, help="Number of contests to schedule (default: 10)")
    parser.add_argument('--algorithm', choices=['greedy', 'welsh_powell', 'dsatur', 'backtracking'], default='dsatur', help="Coloring algorithm (default: dsatur)")
    parser.add_argument('--output', default='output/schedule.json', help="Output JSON file (default: output/schedule.json)")
    parser.add_argument('--time_window_days', type=int, default=3, help="Time window for synthetic contests in days (default: 3)")
    args = parser.parse_args()

    print(f"Fetching up to {args.num_contests} contests from Codeforces API...")
    contests = fetch_contests()
    num_fetched = len(contests)
    print(f"Fetched {num_fetched} contests from API.")
    
    if num_fetched < args.num_contests:
        print(f"Supplementing with {args.num_contests - num_fetched} synthetic contests...")
        synthetic_contests = generate_synthetic_contests(args.num_contests - num_fetched, base_time=contests[0][1]['start_time'] if contests else int(datetime.now().timestamp()), time_window=args.time_window_days * 24 * 3600)
        contests.extend(synthetic_contests)
    
    contests = contests[:args.num_contests]
    print(f"Total contests: {len(contests)}")

    print("Prioritizing contests...")
    contests = prioritize_contests(contests)
    print("Building conflict graph...")
    G = build_conflict_graph(contests)
    print(f"Graph created with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges.")

    print(f"Coloring graph with {args.algorithm} algorithm...")
    if args.algorithm == 'greedy':
        greedy_coloring(G)
    elif args.algorithm == 'welsh_powell':
        welsh_powell_coloring(G)
    elif args.algorithm == 'dsatur':
        dsatur_coloring(G)
    elif args.algorithm == 'backtracking':
        backtracking_coloring(G)

    print("Reordering slots by priority...")
    reorder_slots_by_priority(G)

    num_colors = len(set(data['color'] for _, data in G.nodes(data=True)))
    print(f"\nNumber of slots required: {num_colors}")
    days = assign_slots_to_days(G)
    print(f"Schedule spans {len(days)} days with up to 3 slots per day.")

    print("\nSchedule:")
    for i, day_slots in enumerate(days):
        print(f"\nDay {i+1}:")
        for slot in day_slots:
            print(f"  Slot {slot + 1}:")
            for node, data in G.nodes(data=True):
                if data['color'] == slot:
                    start = datetime.fromtimestamp(data['start_time']).strftime('%Y-%m-%d %H:%M')
                    print(f"    {data['name']} (Start: {start}, Duration: {data['duration']//60} min, Priority: {data['priority']:.2f})")

    save_schedule(G, days, args.output)

    print("\nGenerating visualizations...")
    plot_conflict_graph(G, "output/conflict_graph.png")
    print("Conflict graph saved to conflict_graph.png")
    comparison = compare_algorithms(G)
    plot_algorithm_comparison(comparison, "output/algorithm_comparison.png")
    print("Algorithm comparison saved to algorithm_comparison.png")
    plot_gantt_chart(G, days, "output/schedule_gantt.png")
    print("Gantt chart saved to schedule_gantt.png")

    print("\nAnalytics:")
    analytics = compute_analytics(G, days)
    print(f"Graph Density: {analytics['density']:.3f}")
    print(f"Average Contests per Slot: {analytics['avg_contests_per_slot']:.2f}")
    print(f"Average Priority per Slot: {analytics['avg_priority_per_slot']:.2f}")

    print("\nComparing algorithms...")
    print(f"{'Algorithm':<15} {'Colors':<10} {'Time (s)':<10}")
    print("-" * 35)
    for alg, colors, time_taken in comparison:
        print(f"{alg:<15} {colors:<10} {time_taken:.7f}")

    #Why are we adding a new contest dynamically?
    # Purpose: Competitive programming platforms like Codeforces often 
    # announce new contests with short notice. This feature enables the 
    # scheduler to incorporate such contests without recalculating the 
    # entire schedule from scratch.

    # How: The new contest is added to the conflict graph, and only the 
    # affected parts (e.g., the new contest and its overlapping neighbors) 
    # are re-colored, improving efficiency.

    # Your Context: After scheduling 50 contests into 10 slots (from your 
    # latest analytics: average 5.00 contests/slot), this adds a “Sample Contest” 
    # to test the system’s flexibility.

    print("\nAdding a new contest dynamically...")
    new_contest = (999, {
        'name': 'Sample Contest',
        'start_time': contests[0][1]['start_time'] + 3600 if contests else int(datetime.now().timestamp()),
        'duration': 7200,
        'color': None,
        'priority': 0.9
    })
    add_contest(G, new_contest, args.algorithm)
    reorder_slots_by_priority(G)
    num_colors = len(set(data['color'] for _, data in G.nodes(data=True)))
    print(f"New number of slots required: {num_colors}")
    days = assign_slots_to_days(G)
    updated_filename = "output/updated_schedule.json"
    save_schedule(G, days, updated_filename)

if __name__ == '__main__':
    main()