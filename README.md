ContestSync
ContestSync is a dynamic contest scheduling optimizer designed to manage competitive programming contests using graph coloring techniques. It resolves scheduling conflicts, adapts to real-time contest additions, and provides insightful visualizations and analytics, making it an ideal tool for organizers and participants.
Features

Dynamic Scheduling: Optimizes contest schedules and seamlessly incorporates new contests in real-time.
Graph Coloring Algorithms: Implements Greedy, Welsh-Powell, DSatur, and Backtracking algorithms to minimize scheduling conflicts.
Visualizations: Generates Gantt charts, conflict graphs, and algorithm comparison plots for intuitive analysis.
Analytics: Computes key metrics like graph density, average contests per slot, and priority distribution.
Flexible Configuration: Supports customizable contest counts, time windows, and output file management.

Installation

Clone the Repository:
git clone https://github.com/nitishkrish16/ContestSync.git
cd ContestSync


Set Up a Virtual Environment (recommended):
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate


Install Dependencies:Create a requirements.txt file with:
networkx
matplotlib
pytest

Then install:
pip install -r requirements.txt



Usage
Run the scheduler with the following command:
python scheduler.py --num_contests 10 --algorithm dsatur --output schedule.json --time_window_days 3

Arguments

--num_contests: Number of contests to schedule (default: 10).
--algorithm: Coloring algorithm (options: greedy, welsh_powell, dsatur, backtracking; default: dsatur).
--output: Output JSON file name (default: schedule.json).
--time_window_days: Time window for synthetic contests in days (default: 3).

Example Output
Files are saved in the output/ directory:

output/schedule.json: Initial contest schedule.
output/updated_schedule.json: Schedule after adding a new contest dynamically.
output/conflict_graph.png: Graph visualizing contest conflicts.
output/schedule_gantt.png: Gantt chart of the contest schedule.
output/algorithm_comparison.png: Performance comparison of coloring algorithms.

Project Structure

scheduler.py: Core script for scheduling, dynamic updates, and visualization.
coloring.py: Implements graph coloring algorithms.
api.py: Fetches real contests from Codeforces API and generates synthetic contests.
analytics.py: Handles visualization and analytics generation.
output/: Directory for generated JSON and PNG files (auto-created).
test_contest_scheduler.py: Unit tests for validating functionality.
.gitignore: Excludes output/, venv/, __pycache__, and *.pyc.
README.md: This documentation file.
LICENSE: MIT License file.

Running Tests
Validate functionality with unit tests:
pytest test_contest_scheduler.py -v

This ensures coloring algorithms, synthetic contest generation, and priority reordering work correctly.
Contributing
Contributions are welcome! To contribute:

Fork the repository.
Create a feature branch (git checkout -b feature-branch).
Commit changes (git commit -m "Add feature").
Push to your fork (git push origin feature-branch).
Open a pull request.

Please submit issues or suggestions via GitHub Issues.
License
This project is licensed under the MIT License - see the LICENSE file for details.
Acknowledgments

Inspired by the need to streamline competitive programming contest schedules.
Powered by Python libraries: NetworkX for graph operations, Matplotlib for visualizations, and Pytest for testing.
Thanks to contributors and collaborators for their support.
