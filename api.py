import requests
import networkx as nx
from datetime import datetime, timedelta
import random

def fetch_contests():
    """Fetch upcoming contests from Codeforces API."""
    try:
        response = requests.get("https://codeforces.com/api/contest.list", timeout=5)
        response.raise_for_status()
        contests = response.json()["result"]
        return [(contest["id"], {
            'name': contest["name"],
            'start_time': contest["startTimeSeconds"],
            'duration': contest["durationSeconds"],
            'color': None
        }) for contest in contests if contest["phase"] == "BEFORE"]
    except Exception as e:
        print(f"Error fetching contests: {e}")
        return []

def generate_synthetic_contests(num_contests, base_time, time_window=3*24*3600):
    """Generate synthetic contests within a specified time window."""
    contests = []
    base_date = datetime.fromtimestamp(base_time)
    for i in range(num_contests):
        start_offset = random.randint(0, time_window)  # Within specified time window (e.g., 3 days)
        duration = random.choice([7200, 9000, 10800, 14400])  # 2-4 hours
        contests.append((1000 + i, {
            'name': f"Synthetic Contest #{i+1}",
            'start_time': int((base_date + timedelta(seconds=start_offset)).timestamp()),
            'duration': duration,
            'color': None
        }))
    return contests

def build_conflict_graph(contests):
    """Build a conflict graph based on time overlaps."""
    G = nx.Graph()
    G.add_nodes_from(contests)
    for i, (id1, data1) in enumerate(contests):
        for j, (id2, data2) in enumerate(contests[i+1:], i+1):
            start1, end1 = data1['start_time'], data1['start_time'] + data1['duration']
            start2, end2 = data2['start_time'], data2['start_time'] + data2['duration']
            if not (end1 <= start2 or end2 <= start1):
                G.add_edge(id1, id2)
    return G