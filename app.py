"""
Flask API Server for CPU Scheduler Simulator
Routes:
    GET  /             -> serves index.html frontend
    POST /api/schedule -> run a single scheduling algorithm
    POST /api/compare  -> compare all algorithms side by side
"""

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from scheduler_algorithms import Process, fcfs, sjf, round_robin, priority_scheduling

app = Flask(__name__)
CORS(app)


# ─────────────────────────────────────────────
# ROOT ROUTE  —  serves the HTML frontend
# ─────────────────────────────────────────────
@app.route("/")
def index():
    """
    Serve the main frontend page.
    Place index.html inside a 'templates/' folder next to app.py.

    Folder structure:
        cpu_scheduler/
        ├── app.py
        ├── scheduler_algorithms.py
        ├── requirements.txt
        └── templates/
            └── index.html
    """
    return render_template("index.html")


# ─────────────────────────────────────────────
# HEALTH CHECK  —  quick API status ping
# ─────────────────────────────────────────────
@app.route("/api")
def api_info():
    return jsonify({
        "status": "running",
        "message": "CPU Scheduler API is live!",
        "endpoints": {
            "POST /api/schedule": "Run one scheduling algorithm",
            "POST /api/compare":  "Compare all algorithms at once"
        },
        "supported_algorithms": ["fcfs", "sjf", "rr", "priority"]
    })


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def parse_processes(data):
    """Convert list of dicts from JSON body into Process objects."""
    processes = []
    for p in data:
        pid          = str(p.get("pid", "")).strip()
        arrival_time = int(p.get("arrival_time", 0))
        burst_time   = int(p.get("burst_time", 1))
        priority     = int(p.get("priority", 1))

        if not pid:
            raise ValueError("Each process must have a non-empty 'pid'.")
        if burst_time < 1:
            raise ValueError(f"Process '{pid}': burst_time must be >= 1.")
        if arrival_time < 0:
            raise ValueError(f"Process '{pid}': arrival_time must be >= 0.")
        if priority < 1:
            raise ValueError(f"Process '{pid}': priority must be >= 1.")

        processes.append(Process(
            pid=pid,
            arrival_time=arrival_time,
            burst_time=burst_time,
            priority=priority
        ))
    return processes


def result_to_dict(result):
    """Serialize a SchedulerResult dataclass into a JSON-safe dict."""
    return {
        "gantt": [
            {"pid": g.pid, "start": g.start, "end": g.end}
            for g in result.gantt
        ],
        "waiting_times":     result.waiting_times,
        "turnaround_times":  result.turnaround_times,
        "completion_times":  result.completion_times,
        "avg_waiting_time":  round(result.avg_waiting_time, 2),
        "avg_turnaround_time": round(result.avg_turnaround_time, 2),
        "cpu_utilization":   round(result.cpu_utilization, 2),
        "throughput":        round(result.throughput, 4)
    }


# ─────────────────────────────────────────────
# POST /api/schedule
# ─────────────────────────────────────────────
@app.route("/api/schedule", methods=["POST"])
def schedule():
    """
    Run a single CPU scheduling algorithm.

    Request body (JSON):
    {
        "algorithm": "fcfs",        // fcfs | sjf | rr | priority
        "quantum": 2,               // integer, required for rr
        "processes": [
            {"pid": "P1", "arrival_time": 0, "burst_time": 6, "priority": 2},
            ...
        ]
    }
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body must be valid JSON."}), 400

    processes_data = data.get("processes", [])
    algorithm      = data.get("algorithm", "fcfs").strip().lower()
    quantum        = int(data.get("quantum", 2))

    if not processes_data:
        return jsonify({"error": "No processes provided. Send at least one process."}), 400

    if algorithm not in ("fcfs", "sjf", "rr", "priority"):
        return jsonify({
            "error": f"Unknown algorithm '{algorithm}'.",
            "valid_options": ["fcfs", "sjf", "rr", "priority"]
        }), 400

    if algorithm == "rr" and quantum < 1:
        return jsonify({"error": "quantum must be >= 1 for Round Robin."}), 400

    try:
        processes = parse_processes(processes_data)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    try:
        if algorithm == "fcfs":
            result = fcfs(processes)
        elif algorithm == "sjf":
            result = sjf(processes)
        elif algorithm == "rr":
            result = round_robin(processes, quantum)
        else:
            result = priority_scheduling(processes)

        return jsonify(result_to_dict(result))

    except Exception as e:
        return jsonify({"error": f"Scheduling failed: {str(e)}"}), 500


# ─────────────────────────────────────────────
# POST /api/compare
# ─────────────────────────────────────────────
@app.route("/api/compare", methods=["POST"])
def compare():
    """
    Run all four algorithms on the same process set and return results for each.

    Request body (JSON):
    {
        "quantum": 2,
        "processes": [
            {"pid": "P1", "arrival_time": 0, "burst_time": 6, "priority": 2},
            ...
        ]
    }

    Response: { "fcfs": {...}, "sjf": {...}, "rr": {...}, "priority": {...} }
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body must be valid JSON."}), 400

    processes_data = data.get("processes", [])
    quantum        = int(data.get("quantum", 2))

    if not processes_data:
        return jsonify({"error": "No processes provided."}), 400

    try:
        processes = parse_processes(processes_data)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    try:
        results = {
            "fcfs":     result_to_dict(fcfs(processes)),
            "sjf":      result_to_dict(sjf(processes)),
            "rr":       result_to_dict(round_robin(processes, quantum)),
            "priority": result_to_dict(priority_scheduling(processes))
        }
        return jsonify(results)

    except Exception as e:
        return jsonify({"error": f"Comparison failed: {str(e)}"}), 500


# ─────────────────────────────────────────────
# 404 HANDLER  —  friendly message for bad URLs
# ─────────────────────────────────────────────
@app.errorhandler(404)
def not_found(e):
    return jsonify({
        "error": "Route not found.",
        "hint": "Visit GET / for the frontend, or POST /api/schedule to use the API."
    }), 404


# ─────────────────────────────────────────────
# RUN
# ─────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 50)
    print("  CPU Scheduler API")
    print("  http://127.0.0.1:5000/")
    print("  POST /api/schedule")
    print("  POST /api/compare")
    print("=" * 50)
    app.run(debug=True, port=5000)
