import joblib
import pandas as pd
import numpy as np
import subprocess
import os

# Mapping from ML prediction label → C++ simulator algorithm names
ALGO_MAP = {
    "FCFS":    "FCFS",
    "SJF_NP":  "SJF_NP",
    "SJF_P":   "SJF_P",
    "PRIO_NP": "PRIO_NP",
    "RR":      "RR"
}

def predict_and_run():
    # Load model
    model_path = "cpu_scheduler_model.pkl"
    if not os.path.exists(model_path):
        print(f"Model not found at {model_path}. Please run train_model.py first.")
        return

    model = joblib.load(model_path)

    print("--- ML-Based CPU Scheduling Predictor (Generated Dataset Mode) ---")
    try:
        n = int(input("Enter number of processes: "))
        tq = int(input("Enter Time Quantum (for Round Robin, e.g. 2): "))
    except ValueError:
        print("Invalid input. Please enter numbers.")
        return

    processes = []
    burst_times = []
    arrival_times = []
    priorities = []

    for i in range(n):
        print(f"\nProcess {i+1}:")
        try:
            arr   = int(input("  Arrival Time : "))
            burst = int(input("  Burst Time   : "))
            prio  = int(input("  Priority     : "))
        except ValueError:
            print("Invalid input. Skipping process.")
            continue
            
        processes.append((i+1, arr, burst, prio))
        arrival_times.append(arr)
        burst_times.append(burst)
        priorities.append(prio)

    if not processes:
        print("No processes entered. Exiting.")
        return

    # Features must match training: n_proc, avg_bt, var_bt, avg_at, avg_pr, time_quantum
    features = pd.DataFrame([{
        "n_proc":        len(processes),
        "avg_bt":        np.mean(burst_times),
        "var_bt":        np.var(burst_times),
        "avg_at":        np.mean(arrival_times),
        "avg_pr":        np.mean(priorities),
        "time_quantum":  tq
    }])

    # Predict
    predicted_algo = model.predict(features)[0]
    
    # Try to get probabilities if the model supports it
    try:
        proba = model.predict_proba(features)[0]
        classes = model.classes_
        confidence = max(proba) * 100
        
        print(f"\n{'='*50}")
        print(f" ML PREDICTION  →  {predicted_algo}")
        print(f" CONFIDENCE     →  {confidence:.1f}%")
        print(f"{'='*50}")

        print("\nProbability for each algorithm:")
        for cls, prob in sorted(zip(classes, proba), key=lambda x: -x[1]):
            bar = "█" * int(prob * 30)
            print(f"  {cls:<10} {prob*100:5.1f}%  {bar}")
    except (AttributeError, Exception):
        print(f"\n{'='*50}")
        print(f" ML PREDICTION  →  {predicted_algo}")
        print(f"{'='*50}")

    # Find scheduler.exe
    exe_path = "scheduler.exe"
    if not os.path.exists(exe_path):
        # Check alternate paths
        for candidate in [r"..\scd\main.exe", r"..\scd\scheduler.exe", r"..\scheduler.exe", r"main.exe"]:
            if os.path.exists(candidate):
                exe_path = candidate
                break
        else:
            print("\nError: scheduler.exe (or main.exe) not found.")
            print(r"Ensure scd\main.cpp is compiled to scd\main.exe or ml\scheduler.exe")
            return

    # Run the predicted algorithm
    print(f"\nRunning {predicted_algo} on your processes...")
    cpp_algo = ALGO_MAP.get(predicted_algo, "FCFS")
    cmd = [exe_path, cpp_algo, str(tq)]
    for p in processes:
        cmd.extend([str(p[0]), str(p[1]), str(p[2]), str(p[3])])
        
    try:
        subprocess.run(cmd)
    except Exception as e:
        print(f"Error running scheduler: {e}")

    # Compare with all
    compare = input("\nCompare with ALL algorithms? (y/n): ")
    if compare.lower() == 'y':
        print("\n--- Comparative Analysis ---")
        cmd_all = [exe_path, "ALL", str(tq)]
        for p in processes:
            cmd_all.extend([str(p[0]), str(p[1]), str(p[2]), str(p[3])])
        try:
            subprocess.run(cmd_all)
        except Exception as e:
            print(f"Error running comparison: {e}")

if __name__ == "__main__":
    predict_and_run()
