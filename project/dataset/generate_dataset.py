"""
generate_dataset.py
Generates cpu_dataset.csv by:
 - Randomly sampling workloads (n_proc, burst_times, arrival_times, priorities)
 - Running the C++ scheduler with ALL algorithms for each workload
 - Labeling the row with the algorithm that produced the LOWEST average waiting time
"""

import subprocess   
import random
import csv
import os
import re

# Path to scheduler executable 
SCHEDULER = os.path.abspath(os.path.join("..", "scd", "main.exe"))
OUTPUT_CSV = "cpu_dataset.csv"
NUM_SAMPLES = 5000   # Increase for better model accuracy

ALGORITHMS = ["FCFS", "SJF_NP", "SJF_P", "PRIO_NP", "RR"]

def run_scheduler(algo, processes, quantum=2):
    """Run scheduler and return average waiting time parsed from output."""
    cmd = [SCHEDULER, algo, str(quantum)]
    for p in processes:
        cmd.extend([str(p["pid"]), str(p["arrival"]), str(p["burst"]), str(p["priority"])])

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        output = result.stdout
    except Exception:
        return float("inf")

    # Parse average waiting time from output
    # Expected line like: "Average Waiting Time: 3.50"
    match = re.search(r"Average Waiting Time[:\s]+([0-9.]+)", output)
    if match:
        return float(match.group(1))
    return float("inf")

def generate(): 
    if not os.path.exists(SCHEDULER):
        print(f"Error: Scheduler not found at {SCHEDULER}")
        print("Compile first: g++ -o scd\\main.exe scd\\main.cpp")
        return

    rows = []
    target_per_algo = NUM_SAMPLES // len(ALGORITHMS) 
    counts = {algo: 0 for algo in ALGORITHMS}
    attempts = 0
    max_attempts = NUM_SAMPLES * 20  # Prevent infinite loop

    print(f"Targeting {target_per_algo} samples per algorithm for perfect balance...")

    while sum(counts.values()) < NUM_SAMPLES and attempts < max_attempts:
        attempts += 1
        
        # Randomize workload characteristics
        n  = random.randint(4, 12)
        tq = random.choice([1, 2, 3, 4])

        processes = [{
            "pid":      i + 1,
            "arrival":  random.randint(0, 20),
            "burst":    random.randint(1, 25),
            "priority": random.randint(1, 10) # Wider priority range
        } for i in range(n)]

        burst_times   = [p["burst"]    for p in processes]
        arrival_times = [p["arrival"]  for p in processes]
        priorities    = [p["priority"] for p in processes]

        # Run all algorithms and find the best one
        algo_results = {}
        for algo in ALGORITHMS:
            wt = run_scheduler(algo, processes, quantum=tq)
            algo_results[algo] = wt

        # Tie-breaking: Shuffle algorithms to avoid FCFS bias
        shuffled_algos = list(algo_results.keys())
        random.shuffle(shuffled_algos)
        best_algo = min(shuffled_algos, key=lambda k: algo_results[k])

        # Skip if all runs failed
        if algo_results[best_algo] == float("inf"):
            continue

        # BALANCING LOGIC: Only add if we haven't hit the target for this algo
        if counts[best_algo] < target_per_algo:
            rows.append({
                "n_proc":       n,
                "avg_bt":       sum(burst_times) / n,
                "var_bt":       sum((b - sum(burst_times)/n)**2 for b in burst_times) / n,
                "avg_at":       sum(arrival_times) / n,
                "avg_pr":       sum(priorities) / n,
                "time_quantum": tq,
                "best_algo":    best_algo
            })
            counts[best_algo] += 1
            
            total_gen = sum(counts.values())
            if total_gen % 50 == 0:
                print(f"Progress: {total_gen}/{NUM_SAMPLES} samples collected. Current counts: {counts}")

    # Write CSV
    if rows:
        with open(OUTPUT_CSV, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
        print(f"\n✅ Balanced Dataset saved to {OUTPUT_CSV} ({len(rows)} rows)")
        
        print("\nFinal Class Distribution:")
        for algo, count in sorted(counts.items(), key=lambda x: -x[1]):
            print(f"  {algo:<10}: {count}")
    else:
        print("No rows generated. Check if scheduler.exe works.")

if __name__ == "__main__":
    generate()
