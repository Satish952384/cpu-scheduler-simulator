<<<<<<< HEAD
# cpu-scheduler-simulator
Intelligent CPU Scheduler Simulator using Flask
=======
# Intelligent CPU Scheduler Simulator

A full-featured CPU scheduling simulator with real-time Gantt chart visualization,
performance metrics, algorithm comparison, and AI-powered analysis.

---

## Features

- **4 Scheduling Algorithms**: FCFS, SJF, Round Robin, Priority Scheduling
- **Gantt Chart Visualization**: Color-coded, real-time SVG charts
- **Performance Metrics**: Avg Waiting Time, Avg Turnaround Time, CPU Utilization, Throughput
- **Per-Process Detail Table**: Completion, Waiting, Turnaround per process
- **Compare All Algorithms**: Side-by-side metrics and mini Gantt charts
- **Bar Charts**: Visual comparison of waiting and turnaround times
- **AI Analysis**: Uses Claude AI to explain results, detect starvation, suggest optimizations

---

## Project Structure

```
cpu_scheduler/
├── index.html               # Standalone full-stack frontend (open directly in browser)
├── scheduler_algorithms.py  # Pure Python scheduling algorithms module
├── app.py                   # Flask REST API backend
├── requirements.txt         # Python dependencies
└── README.md
```

---

## Quick Start (No Server Needed)

Just open `index.html` in your browser. All scheduling runs in JavaScript.
AI analysis requires the browser to have API access (works in Claude.ai artifacts).

---

## Flask Backend Setup

```bash
pip install -r requirements.txt
python app.py
```

Server runs at `http://localhost:5000`

### API Endpoints

**POST /api/schedule**
```json
{
  "algorithm": "fcfs",        // fcfs | sjf | rr | priority
  "quantum": 2,               // for Round Robin only
  "processes": [
    {"pid": "P1", "arrival_time": 0, "burst_time": 6, "priority": 2}
  ]
}
```

Response:
```json
{
  "gantt": [{"pid": "P1", "start": 0, "end": 6}],
  "waiting_times": {"P1": 0},
  "turnaround_times": {"P1": 6},
  "completion_times": {"P1": 6},
  "avg_waiting_time": 0.0,
  "avg_turnaround_time": 6.0,
  "cpu_utilization": 100.0,
  "throughput": 0.1667
}
```

**POST /api/compare** — runs all 4 algorithms and returns results for each.

---

## Algorithm Details

### FCFS (First Come First Served)
- Non-preemptive
- Processes run in order of arrival
- Simple but can cause convoy effect (long waiting for short jobs)

### SJF (Shortest Job First)
- Non-preemptive
- Picks the shortest available job at each decision point
- Minimizes average waiting time
- Risk: starvation of long processes

### Round Robin
- Preemptive, time-sliced
- Each process gets a fixed time quantum
- Fair scheduling; good for time-sharing systems
- Adjust quantum with the Time Quantum input

### Priority Scheduling
- Non-preemptive
- Lower priority number = higher priority
- Risk: starvation of low-priority processes
- Best for real-time systems with known priorities

---

## Performance Metrics Explained

| Metric | Formula |
|--------|---------|
| Waiting Time | Turnaround Time - Burst Time |
| Turnaround Time | Completion Time - Arrival Time |
| CPU Utilization | (Total Burst Time / Total Duration) × 100% |
| Throughput | Number of Processes / Total Time |

---

## Using the Python Module Directly

```python
from scheduler_algorithms import Process, fcfs, sjf, round_robin, priority_scheduling

processes = [
    Process(pid="P1", arrival_time=0, burst_time=6, priority=2),
    Process(pid="P2", arrival_time=1, burst_time=4, priority=1),
    Process(pid="P3", arrival_time=2, burst_time=8, priority=3),
]

result = fcfs(processes)
print(f"Avg Waiting Time: {result.avg_waiting_time:.2f}")
print(f"Avg Turnaround Time: {result.avg_turnaround_time:.2f}")
print(f"CPU Utilization: {result.cpu_utilization:.1f}%")

for entry in result.gantt:
    print(f"  {entry.pid}: {entry.start} → {entry.end}")
```

---

## AI Analysis

The AI Analyze button sends your process data and results to Claude (Anthropic API).
It explains:
1. Algorithm behavior for the specific workload
2. Starvation risk and fairness observations
3. Recommended algorithm for the workload
4. Optimization suggestions

Works natively in Claude.ai artifacts or with a valid Anthropic API key.
>>>>>>> 2f20c5c (CPU Scheduler Project)
