#include <iostream>
#include <vector>
#include <algorithm>
#include <iomanip>
#include <queue>
#include <map>

using namespace std;

struct Process {
    int id;
    int arrival_time;
    int burst_time;
    int remaining_time;
    int priority;
    int completion_time;
    int waiting_time;
    int turnaround_time;
    int start_time;
};

struct GanttItem {
    int process_id;
    int start;
    int end;
};

void printGanttChart(const vector<GanttItem>& gantt) {
    if (gantt.empty()) return;

    cout << "\nGantt Chart:" << endl;
    
    // Top bar
    cout << " ";
    for (const auto& item : gantt) {
        int width = max(4, (item.end - item.start) * 2 + 2);
        for (int i = 0; i < width; i++) cout << "-";
        cout << " ";
    }
    cout << endl << "|";

    // Process IDs
    for (const auto& item : gantt) {
        int width = max(4, (item.end - item.start) * 2 + 2);
        string pid = "P" + to_string(item.process_id);
        int padding = (width - pid.length()) / 2;
        for (int i = 0; i < padding; i++) cout << " ";
        cout << pid;
        for (int i = 0; i < width - padding - pid.length(); i++) cout << " ";
        cout << "|";
    }
    cout << endl << " ";

    // Bottom bar
    for (const auto& item : gantt) {
        int width = max(4, (item.end - item.start) * 2 + 2);
        for (int i = 0; i < width; i++) cout << "-";
        cout << " ";
    }
    cout << endl;

    // Time scale
    cout << gantt[0].start;
    for (const auto& item : gantt) {
        int width = max(4, (item.end - item.start) * 2 + 2);
        cout << setw(width + 1) << right << item.end;
    }
    cout << endl;
}

void printMetrics(const vector<Process>& processes, const vector<GanttItem>& gantt, const string& algo_name) {
    double total_wt = 0, total_tat = 0;
    for (const auto& p : processes) {
        total_wt += p.waiting_time;
        total_tat += p.turnaround_time;
    }

    cout << "\nAlgorithm: " << algo_name << endl;
    cout << "--------------------------------------------------" << endl;
    cout << "PID\tArr\tBurst\tPrio\tComp\tTAT\tWT" << endl;
    for (const auto& p : processes) {
        cout << p.id << "\t" << p.arrival_time << "\t" << p.burst_time << "\t" << p.priority 
             << "\t" << p.completion_time << "\t" << p.turnaround_time << "\t" << p.waiting_time << endl;
    }
    
    cout << fixed << setprecision(2);
    cout << "\nAverage Waiting Time: " << total_wt / processes.size() << endl;
    cout << "Average Turnaround Time: " << total_tat / processes.size() << endl;

    printGanttChart(gantt);

    // Minimal CSV-like output for Python to parse
    cout << "\nRESULT_AVG_WT:" << total_wt / processes.size() << endl;
}

// FCFS
void runFCFS(vector<Process> processes) {
    sort(processes.begin(), processes.end(), [](Process a, Process b) {
        return a.arrival_time < b.arrival_time;
    });

    int current_time = 0;
    vector<GanttItem> gantt;
    for (auto& p : processes) {
        if (current_time < p.arrival_time) current_time = p.arrival_time;
        p.start_time = current_time;
        p.completion_time = current_time + p.burst_time;
        p.turnaround_time = p.completion_time - p.arrival_time;
        p.waiting_time = p.turnaround_time - p.burst_time;
        gantt.push_back({p.id, current_time, p.completion_time});
        current_time = p.completion_time;
    }
    printMetrics(processes, gantt, "FCFS");
}

// SJF Non-Preemptive
void runSJF_NP(vector<Process> processes) {
    int n = processes.size();
    int completed = 0, current_time = 0;
    vector<bool> is_completed(n, false);
    vector<GanttItem> gantt;

    while (completed != n) {
        int idx = -1;
        int min_burst = 1e9;
        for (int i = 0; i < n; i++) {
            if (processes[i].arrival_time <= current_time && !is_completed[i]) {
                if (processes[i].burst_time < min_burst) {
                    min_burst = processes[i].burst_time;
                    idx = i;
                }
                if (processes[i].burst_time == min_burst) {
                    if (processes[i].arrival_time < processes[idx].arrival_time) {
                        idx = i;
                    }
                }
            }
        }

        if (idx != -1) {
            processes[idx].start_time = current_time;
            processes[idx].completion_time = current_time + processes[idx].burst_time;
            processes[idx].turnaround_time = processes[idx].completion_time - processes[idx].arrival_time;
            processes[idx].waiting_time = processes[idx].turnaround_time - processes[idx].burst_time;
            gantt.push_back({processes[idx].id, current_time, processes[idx].completion_time});
            current_time = processes[idx].completion_time;
            is_completed[idx] = true;
            completed++;
        } else {
            current_time++;
        }
    }
    printMetrics(processes, gantt, "SJF_NP");
}

// Priority Non-Preemptive
void runPriority_NP(vector<Process> processes) {
    int n = processes.size();
    int completed = 0, current_time = 0;
    vector<bool> is_completed(n, false);
    vector<GanttItem> gantt;

    while (completed != n) {
        int idx = -1;
        int max_prio = 1e9;
        for (int i = 0; i < n; i++) {
            if (processes[i].arrival_time <= current_time && !is_completed[i]) {
                if (processes[i].priority < max_prio) {
                    max_prio = processes[i].priority;
                    idx = i;
                }
                if (processes[i].priority == max_prio) {
                    if (processes[i].arrival_time < processes[idx].arrival_time) {
                        idx = i;
                    }
                }
            }
        }

        if (idx != -1) {
            processes[idx].start_time = current_time;
            processes[idx].completion_time = current_time + processes[idx].burst_time;
            processes[idx].turnaround_time = processes[idx].completion_time - processes[idx].arrival_time;
            processes[idx].waiting_time = processes[idx].turnaround_time - processes[idx].burst_time;
            gantt.push_back({processes[idx].id, current_time, processes[idx].completion_time});
            current_time = processes[idx].completion_time;
            is_completed[idx] = true;
            completed++;
        } else {
            current_time++;
        }
    }
    printMetrics(processes, gantt, "Priority_NP");
}

// RR
void runRR(vector<Process> processes, int quantum) {
    int n = processes.size();
    queue<int> q;
    vector<int> rem_bt(n);
    for(int i=0; i<n; i++) rem_bt[i] = processes[i].burst_time;
    
    sort(processes.begin(), processes.end(), [](Process a, Process b) {
        return a.arrival_time < b.arrival_time;
    });

    int current_time = 0;
    int completed = 0;
    vector<bool> in_queue(n, false);
    vector<GanttItem> gantt;

    q.push(0);
    in_queue[0] = true;

    while (completed != n) {
        if (q.empty()) {
            current_time++;
            for(int i=0; i<n; i++) {
                if(processes[i].arrival_time <= current_time && !in_queue[i] && rem_bt[i] > 0) {
                    q.push(i);
                    in_queue[i] = true;
                    break;
                }
            }
            continue;
        }

        int idx = q.front();
        q.pop();

        int exec_time = min(rem_bt[idx], quantum);
        gantt.push_back({processes[idx].id, current_time, current_time + exec_time});
        current_time += exec_time;
        rem_bt[idx] -= exec_time;

        for(int i=0; i<n; i++) {
            if(processes[i].arrival_time <= current_time && !in_queue[i] && rem_bt[i] > 0) {
                q.push(i);
                in_queue[i] = true;
            }
        }

        if (rem_bt[idx] > 0) {
            q.push(idx);
        } else {
            processes[idx].completion_time = current_time;
            processes[idx].turnaround_time = processes[idx].completion_time - processes[idx].arrival_time;
            processes[idx].waiting_time = processes[idx].turnaround_time - processes[idx].burst_time;
            completed++;
        }
    }
    printMetrics(processes, gantt, "Round Robin (Q=" + to_string(quantum) + ")");
}

// SJF Preemptive (SRTF)
void runSJF_P(vector<Process> processes) {
    int n = processes.size();
    int completed = 0, current_time = 0;
    vector<int> rem_bt(n);
    for(int i=0; i<n; i++) rem_bt[i] = processes[i].burst_time;
    vector<GanttItem> gantt;
    int last_idx = -1;

    while (completed != n) {
        int idx = -1;
        int min_bt = 1e9;
        for (int i = 0; i < n; i++) {
            if (processes[i].arrival_time <= current_time && rem_bt[i] > 0) {
                if (rem_bt[i] < min_bt) {
                    min_bt = rem_bt[i];
                    idx = i;
                }
                if (rem_bt[i] == min_bt) {
                    if (processes[i].arrival_time < processes[idx].arrival_time) {
                        idx = i;
                    }
                }
            }
        }

        if (idx != -1) {
            if (last_idx != idx) {
                gantt.push_back({processes[idx].id, current_time, current_time + 1});
            } else {
                gantt.back().end++;
            }
            
            rem_bt[idx]--;
            current_time++;
            last_idx = idx;

            if (rem_bt[idx] == 0) {
                processes[idx].completion_time = current_time;
                processes[idx].turnaround_time = processes[idx].completion_time - processes[idx].arrival_time;
                processes[idx].waiting_time = processes[idx].turnaround_time - processes[idx].burst_time;
                completed++;
                last_idx = -1;
            }
        } else {
            current_time++;
        }
    }
    printMetrics(processes, gantt, "SJF_Preemptive");
}

int main(int argc, char* argv[]) {
    string algo;
    int quantum = 2;
    vector<Process> processes;

    if (argc >= 3) {
        algo = argv[1];
        quantum = stoi(argv[2]);
        for (int i = 3; i + 3 < argc; i += 4) {
            processes.push_back({stoi(argv[i]), stoi(argv[i+1]), stoi(argv[i+2]), stoi(argv[i+2]), stoi(argv[i+3]), 0, 0, 0, 0});
        }
    } else {
        cout << "--- CPU Scheduling Simulator ---" << endl;
        cout << "Select Algorithm (FCFS, SJF_NP, SJF_P, PRIO_NP, RR, ALL): ";
        cin >> algo;
        
        if (algo == "RR" || algo == "ALL") {
            cout << "Enter Time Quantum: ";
            cin >> quantum;
        }

        int n;
        cout << "Enter number of processes: ";
        cin >> n;

        for (int i = 0; i < n; i++) {
            int id, arr, burst, prio;
            cout << "\nProcess " << i + 1 << ":" << endl;
            cout << "PID: "; cin >> id;
            cout << "Arrival Time: "; cin >> arr;
            cout << "Burst Time: "; cin >> burst;
            cout << "Priority: "; cin >> prio;
            processes.push_back({id, arr, burst, burst, prio, 0, 0, 0, 0});
        }
    }

    if (processes.empty()) return 1;

    if (algo == "FCFS") runFCFS(processes);
    else if (algo == "SJF_NP") runSJF_NP(processes);
    else if (algo == "SJF_P") runSJF_P(processes);
    else if (algo == "PRIO_NP") runPriority_NP(processes);
    else if (algo == "RR") runRR(processes, quantum);
    else if (algo == "ALL") {
        runFCFS(processes);
        runSJF_NP(processes);
        runSJF_P(processes);
        runPriority_NP(processes);
        runRR(processes, quantum);
    } else {
        cout << "Invalid algorithm selected." << endl;
    }

    return 0;
}
