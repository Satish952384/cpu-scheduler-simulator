"""
CPU Scheduling Algorithms Module
=================================
Implements four classic CPU scheduling algorithms:
    - FCFS     : First Come First Served (non-preemptive)
    - SJF      : Shortest Job First     (non-preemptive)
    - RR       : Round Robin            (preemptive, time-sliced)
    - Priority : Priority Scheduling    (non-preemptive, lower number = higher priority)

Usage:
    from scheduler_algorithms import Process, fcfs, sjf, round_robin, priority_scheduling

    processes = [
        Process(pid="P1", arrival_time=0, burst_time=6, priority=2),
        Process(pid="P2", arrival_time=1, burst_time=4, priority=1),
    ]
    result = fcfs(processes)
    print(result.avg_waiting_time)
    print(result.gantt)
"""

from dataclasses import dataclass, field
from typing import List, Dict
import copy


# ─────────────────────────────────────────────
# DATA CLASSES
# ─────────────────────────────────────────────

@dataclass
class Process:
    pid:            str
    arrival_time:   int
    burst_time:     int
    priority:       int
    remaining_time: int = field(default=0, init=True)

    def __post_init__(self):
        self.remaining_time = self.burst_time


@dataclass
class GanttEntry:
    pid:   str
    start: int
    end:   int


@dataclass
class SchedulerResult:
    gantt:               List[GanttEntry]
    waiting_times:       Dict[str, float]
    turnaround_times:    Dict[str, float]
    completion_times:    Dict[str, int]
    avg_waiting_time:    float
    avg_turnaround_time: float
    cpu_utilization:     float
    throughput:          float


# ─────────────────────────────────────────────
# ALGORITHM 1 — FCFS
# ─────────────────────────────────────────────

def fcfs(processes: List[Process]) -> SchedulerResult:
    if not processes:
        raise ValueError("Process list cannot be empty.")

    sorted_procs = sorted(copy.deepcopy(processes), key=lambda p: (p.arrival_time, p.pid))
    time = 0
    gantt = []
    comp_times = {}

    for p in sorted_procs:
        if time < p.arrival_time:
            time = p.arrival_time
        start = time
        time += p.burst_time
        gantt.append(GanttEntry(pid=p.pid, start=start, end=time))
        comp_times[p.pid] = time

    return _compute_metrics(processes, gantt, comp_times)


# ─────────────────────────────────────────────
# ALGORITHM 2 — SJF
# ─────────────────────────────────────────────

def sjf(processes: List[Process]) -> SchedulerResult:
    if not processes:
        raise ValueError("Process list cannot be empty.")

    procs = copy.deepcopy(processes)
    time = 0
    gantt = []
    comp_times = {}
    done = set()

    while len(done) < len(procs):
        available = [p for p in procs if p.arrival_time <= time and p.pid not in done]

        if not available:
            time = min(p.arrival_time for p in procs if p.pid not in done)
            continue

        p = min(available, key=lambda x: (x.burst_time, x.arrival_time, x.pid))
        start = time
        time += p.burst_time
        gantt.append(GanttEntry(pid=p.pid, start=start, end=time))
        comp_times[p.pid] = time
        done.add(p.pid)

    return _compute_metrics(processes, gantt, comp_times)


# ─────────────────────────────────────────────
# ALGORITHM 3 — Round Robin
# ─────────────────────────────────────────────

def round_robin(processes: List[Process], quantum: int = 2) -> SchedulerResult:
    if not processes:
        raise ValueError("Process list cannot be empty.")
    if quantum < 1:
        raise ValueError("Time quantum must be >= 1.")

    procs = copy.deepcopy(processes)
    for p in procs:
        p.remaining_time = p.burst_time

    proc_map = {p.pid: p for p in procs}
    sorted_by_arrival = sorted(procs, key=lambda p: (p.arrival_time, p.pid))

    time = 0
    gantt = []
    comp_times = {}
    done = set()
    queue = []
    arrived = set()

    for p in sorted_by_arrival:
        if p.arrival_time <= time:
            queue.append(p.pid)
            arrived.add(p.pid)

    guard = 0

    while len(done) < len(procs) and guard < 200_000:
        guard += 1

        if not queue:
            not_done_not_arrived = [
                p for p in sorted_by_arrival
                if p.pid not in done and p.pid not in arrived
            ]
            if not not_done_not_arrived:
                break
            time = not_done_not_arrived[0].arrival_time
            for p in sorted_by_arrival:
                if p.arrival_time <= time and p.pid not in arrived and p.pid not in done:
                    queue.append(p.pid)
                    arrived.add(p.pid)
            continue

        pid = queue.pop(0)
        p = proc_map[pid]
        run_time = min(quantum, p.remaining_time)
        start = time
        time += run_time
        p.remaining_time -= run_time

        gantt.append(GanttEntry(pid=pid, start=start, end=time))

        for proc in sorted_by_arrival:
            if (proc.pid not in arrived
                    and proc.pid not in done
                    and proc.pid != pid
                    and proc.arrival_time <= time):
                queue.append(proc.pid)
                arrived.add(proc.pid)

        if p.remaining_time == 0:
            comp_times[pid] = time
            done.add(pid)
        else:
            queue.append(pid)

    return _compute_metrics(processes, gantt, comp_times)


# ─────────────────────────────────────────────
# ALGORITHM 4 — Priority Scheduling
# ─────────────────────────────────────────────

def priority_scheduling(processes: List[Process]) -> SchedulerResult:
    if not processes:
        raise ValueError("Process list cannot be empty.")

    procs = copy.deepcopy(processes)
    time = 0
    gantt = []
    comp_times = {}
    done = set()

    while len(done) < len(procs):
        available = [p for p in procs if p.arrival_time <= time and p.pid not in done]

        if not available:
            time = min(p.arrival_time for p in procs if p.pid not in done)
            continue

        p = min(available, key=lambda x: (x.priority, x.arrival_time, x.pid))
        start = time
        time += p.burst_time
        gantt.append(GanttEntry(pid=p.pid, start=start, end=time))
        comp_times[p.pid] = time
        done.add(p.pid)

    return _compute_metrics(processes, gantt, comp_times)


# ─────────────────────────────────────────────
# SHARED METRIC CALCULATOR
# ─────────────────────────────────────────────

def _compute_metrics(
    original_processes: List[Process],
    gantt: List[GanttEntry],
    comp_times: Dict[str, int]
) -> SchedulerResult:

    waiting_times = {}
    turnaround_times = {}

    for p in original_processes:
        ct  = comp_times[p.pid]
        tat = ct - p.arrival_time
        wt  = tat - p.burst_time
        turnaround_times[p.pid] = tat
        waiting_times[p.pid]    = max(0, wt)

    n       = len(original_processes)
    avg_wt  = sum(waiting_times.values())    / n
    avg_tat = sum(turnaround_times.values()) / n

    start_time = min(p.arrival_time for p in original_processes)
    end_time   = max(comp_times.values())
    total_span = end_time - start_time
    busy_time  = sum(p.burst_time for p in original_processes)

    cpu_util   = (busy_time / total_span * 100) if total_span > 0 else 100.0
    throughput = n / end_time if end_time > 0 else 0.0

    return SchedulerResult(
        gantt               = gantt,
        waiting_times       = waiting_times,
        turnaround_times    = turnaround_times,
        completion_times    = comp_times,
        avg_waiting_time    = avg_wt,
        avg_turnaround_time = avg_tat,
        cpu_utilization     = cpu_util,
        throughput          = throughput
    )
