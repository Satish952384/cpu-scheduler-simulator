"""
test_api.py
============
Run this script while your Flask server is running to test all API endpoints.

Usage:
    python app.py          # start the server in one terminal
    python test_api.py     # run tests in another terminal

Requirements:
    pip install requests
"""

import json
import sys

try:
    import requests
except ImportError:
    print("ERROR: 'requests' not installed. Run: pip install requests")
    sys.exit(1)

BASE_URL = "http://127.0.0.1:5000"

# ─── Sample processes used in all tests ───────────────────────────────────────
SAMPLE_PROCESSES = [
    {"pid": "P1", "arrival_time": 0, "burst_time": 6, "priority": 2},
    {"pid": "P2", "arrival_time": 1, "burst_time": 4, "priority": 1},
    {"pid": "P3", "arrival_time": 2, "burst_time": 8, "priority": 3},
    {"pid": "P4", "arrival_time": 3, "burst_time": 3, "priority": 2},
    {"pid": "P5", "arrival_time": 4, "burst_time": 5, "priority": 1},
]


def pretty(data):
    print(json.dumps(data, indent=2))


def separator(title):
    print("\n" + "=" * 55)
    print(f"  {title}")
    print("=" * 55)


# ─── TEST 1: Root route ────────────────────────────────────────────────────────
def test_root():
    separator("GET / — Root Route")
    r = requests.get(f"{BASE_URL}/")
    print(f"Status : {r.status_code}")
    # Root serves HTML; just check it doesn't 404
    if r.status_code == 200:
        print("PASSED — root route is working (no 404)")
    else:
        print(f"FAILED — got status {r.status_code}")


# ─── TEST 2: Health check ──────────────────────────────────────────────────────
def test_health():
    separator("GET /api — Health Check")
    r = requests.get(f"{BASE_URL}/api")
    print(f"Status : {r.status_code}")
    pretty(r.json())


# ─── TEST 3: FCFS ─────────────────────────────────────────────────────────────
def test_fcfs():
    separator("POST /api/schedule — FCFS")
    payload = {
        "algorithm": "fcfs",
        "processes": SAMPLE_PROCESSES
    }
    r = requests.post(f"{BASE_URL}/api/schedule", json=payload)
    print(f"Status : {r.status_code}")
    data = r.json()
    print(f"Avg Waiting Time    : {data['avg_waiting_time']}")
    print(f"Avg Turnaround Time : {data['avg_turnaround_time']}")
    print(f"CPU Utilization     : {data['cpu_utilization']}%")
    print(f"Throughput          : {data['throughput']}")
    print("\nGantt Chart:")
    for g in data["gantt"]:
        bar = "█" * (g["end"] - g["start"])
        print(f"  {g['pid']}  [{g['start']:>3} → {g['end']:>3}]  {bar}")


# ─── TEST 4: SJF ──────────────────────────────────────────────────────────────
def test_sjf():
    separator("POST /api/schedule — SJF")
    payload = {
        "algorithm": "sjf",
        "processes": SAMPLE_PROCESSES
    }
    r = requests.post(f"{BASE_URL}/api/schedule", json=payload)
    print(f"Status : {r.status_code}")
    data = r.json()
    print(f"Avg Waiting Time    : {data['avg_waiting_time']}")
    print(f"Avg Turnaround Time : {data['avg_turnaround_time']}")
    print("\nGantt Chart:")
    for g in data["gantt"]:
        bar = "█" * (g["end"] - g["start"])
        print(f"  {g['pid']}  [{g['start']:>3} → {g['end']:>3}]  {bar}")


# ─── TEST 5: Round Robin ──────────────────────────────────────────────────────
def test_round_robin():
    separator("POST /api/schedule — Round Robin (quantum=2)")
    payload = {
        "algorithm": "rr",
        "quantum": 2,
        "processes": SAMPLE_PROCESSES
    }
    r = requests.post(f"{BASE_URL}/api/schedule", json=payload)
    print(f"Status : {r.status_code}")
    data = r.json()
    print(f"Avg Waiting Time    : {data['avg_waiting_time']}")
    print(f"Avg Turnaround Time : {data['avg_turnaround_time']}")
    print("\nGantt Chart:")
    for g in data["gantt"]:
        bar = "█" * (g["end"] - g["start"])
        print(f"  {g['pid']}  [{g['start']:>3} → {g['end']:>3}]  {bar}")


# ─── TEST 6: Priority Scheduling ──────────────────────────────────────────────
def test_priority():
    separator("POST /api/schedule — Priority Scheduling")
    payload = {
        "algorithm": "priority",
        "processes": SAMPLE_PROCESSES
    }
    r = requests.post(f"{BASE_URL}/api/schedule", json=payload)
    print(f"Status : {r.status_code}")
    data = r.json()
    print(f"Avg Waiting Time    : {data['avg_waiting_time']}")
    print(f"Avg Turnaround Time : {data['avg_turnaround_time']}")
    print("\nGantt Chart:")
    for g in data["gantt"]:
        bar = "█" * (g["end"] - g["start"])
        print(f"  {g['pid']}  [{g['start']:>3} → {g['end']:>3}]  {bar}")


# ─── TEST 7: Compare All ──────────────────────────────────────────────────────
def test_compare():
    separator("POST /api/compare — All Algorithms")
    payload = {
        "quantum": 2,
        "processes": SAMPLE_PROCESSES
    }
    r = requests.post(f"{BASE_URL}/api/compare", json=payload)
    print(f"Status : {r.status_code}")
    data = r.json()

    labels = {"fcfs": "FCFS", "sjf": "SJF", "rr": "Round Robin", "priority": "Priority"}
    print(f"\n{'Algorithm':<15} {'Avg Wait':>10} {'Avg TAT':>10} {'CPU Util':>10} {'Throughput':>12}")
    print("-" * 60)
    for key, label in labels.items():
        d = data[key]
        print(f"{label:<15} {d['avg_waiting_time']:>10.2f} {d['avg_turnaround_time']:>10.2f} "
              f"{d['cpu_utilization']:>9.1f}% {d['throughput']:>12.4f}")


# ─── TEST 8: Error handling — empty processes ──────────────────────────────────
def test_empty_processes():
    separator("Error Handling — Empty Process List")
    payload = {"algorithm": "fcfs", "processes": []}
    r = requests.post(f"{BASE_URL}/api/schedule", json=payload)
    print(f"Status  : {r.status_code}  (expected 400)")
    print(f"Response: {r.json()}")


# ─── TEST 9: Error handling — unknown algorithm ───────────────────────────────
def test_unknown_algorithm():
    separator("Error Handling — Unknown Algorithm")
    payload = {"algorithm": "mystery_algo", "processes": SAMPLE_PROCESSES}
    r = requests.post(f"{BASE_URL}/api/schedule", json=payload)
    print(f"Status  : {r.status_code}  (expected 400)")
    print(f"Response: {r.json()}")


# ─── TEST 10: 404 handler ─────────────────────────────────────────────────────
def test_404():
    separator("Error Handling — 404 on Unknown Route")
    r = requests.get(f"{BASE_URL}/this/does/not/exist")
    print(f"Status  : {r.status_code}  (expected 404)")
    print(f"Response: {r.json()}")


# ─── RUN ALL TESTS ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\nCPU Scheduler API — Test Suite")
    print(f"Connecting to: {BASE_URL}")

    try:
        requests.get(BASE_URL, timeout=2)
    except requests.ConnectionError:
        print(f"\nERROR: Cannot connect to {BASE_URL}")
        print("Make sure Flask is running:  python app.py")
        sys.exit(1)

    test_root()
    test_health()
    test_fcfs()
    test_sjf()
    test_round_robin()
    test_priority()
    test_compare()
    test_empty_processes()
    test_unknown_algorithm()
    test_404()

    print("\n" + "=" * 55)
    print("  All tests complete!")
    print("=" * 55 + "\n")
