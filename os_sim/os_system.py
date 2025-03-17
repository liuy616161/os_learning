#!/usr/bin/env python3
import sys
import importlib.util
import time
import argparse
from typing import Dict, List, Generator, Any, Tuple
import random
import os
from collections import deque

class Process:
    """Represents a process in the operating system"""
    def __init__(self, pid: int, name: str, generator: Generator, priority: int = None):
        self.pid = pid
        self.name = name
        self.generator = generator  # Using generator for cooperative multitasking
        self.state = "ready"  # ready, running, waiting, terminated
        self.priority = priority if priority is not None else random.randint(1, 10)
        self.arrival_time = 0  # Clock time when process was created
        self.start_time = None  # Clock time when process first ran
        self.end_time = None  # Clock time when process terminated
        self.cpu_time = 0  # Total CPU time used
        self.last_run_time = None  # Last clock time when the process started running
        self.return_value = None
        self.estimated_burst_time = random.randint(3, 10)  # Estimated CPU burst time
        self.executed_steps = 0  # Number of steps executed
        self.waiting_time = 0  # Process waiting time (total time in ready state)
        self.turnaround_time = 0  # Turnaround time
        self.run_history = []  # Record of process execution history
        self.quantum_remaining = 0  # Remaining time quantum for Round Robin
        self.current_burst = 0  # Current CPU burst (work units)
        self.current_slice = 0  # Current time slice used in this run
        self.current_run_start = None  # Start time of current run for drawing Gantt chart

    def __str__(self):
        return f"Process(pid={self.pid}, name={self.name}, state={self.state}, priority={self.priority})"

class SimpleOS:
    """Simple operating system simulation with multiple scheduling algorithms"""
    def __init__(self, scheduler_type="round_robin", time_quantum=5, visualize=False, time_slice=1):
        self.processes: Dict[int, Process] = {}
        self.ready_queue = deque()  # Queue for FCFS and Round Robin
        self.current_pid = 0
        self.running_process = None
        self.last_running_pid = None  # Track the last running process for context switches
        self.clock = 0
        self.terminated_processes: List[Process] = []
        self.scheduler_type = scheduler_type
        self.time_quantum = time_quantum  # Time quantum for Round Robin
        self.time_slice = time_slice  # Minimum time slice for execution
        self.visualize = visualize
        self.execution_log = []  # For visualization
        self.context_switches = 0
        
        print(f"Initializing OS with {self.scheduler_type} scheduler")
        print(f"Time slice granularity: {self.time_slice} units")
        if self.scheduler_type == "round_robin":
            print(f"Time quantum: {self.time_quantum} units")

    def load_program(self, file_path: str, priority: int = None) -> int:
        """Load a Python program as a process"""
        try:
            # Extract module name from file path
            module_name = file_path.split('/')[-1]
            if module_name.endswith('.py'):
                module_name = module_name[:-3]
            
            # Load Python module
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            if spec is None or spec.loader is None:
                print(f"Error: Could not load {file_path}")
                return -1
                
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Check if the module has a main function
            if not hasattr(module, 'main') or not callable(module.main):
                print(f"Error: {file_path} does not have a main() function")
                return -1
            
            # Create process
            pid = self._create_process(module_name, module.main(), priority)
            print(f"Process {pid} ({module_name}) loaded successfully, priority: {self.processes[pid].priority}")
            return pid
        except Exception as e:
            print(f"Error loading program: {e}")
            return -1

    def _create_process(self, name: str, generator: Generator, priority: int = None) -> int:
        """Create a new process"""
        self.current_pid += 1
        process = Process(self.current_pid, name, generator, priority)
        process.arrival_time = self.clock
        
        self.processes[self.current_pid] = process
        
        # For Round Robin, initialize time quantum
        if self.scheduler_type == "round_robin":
            process.quantum_remaining = self.time_quantum
            
        # Add to ready queue
        self.ready_queue.append(self.current_pid)
        
        return self.current_pid

    def run(self):
        """Run the OS scheduler"""
        print("\nStarting OS...")
        print("=" * 50)
        print(f"Scheduler: {self.scheduler_type}")
        
        # Process scheduling loop
        while self.processes:
            # Select next process to run
            pid = self._scheduler()
            if pid is None:
                break
                
            process = self.processes[pid]
            
            # Check for context switch - only count when switching between different processes
            if self.last_running_pid is not None and self.last_running_pid != pid:
                self.context_switches += 1
                print(f"[Clock:{self.clock}] Context switch: {self.last_running_pid} -> {pid}")
                
            # Update waiting time for all ready processes except the one about to run
            self._update_waiting_times(pid)
            
            # If this is a new run for the process
            if process.state == "ready" or self.last_running_pid != pid:
                process.state = "running"
                process.last_run_time = self.clock
                process.current_run_start = self.clock  # Start time for Gantt chart
                
                # If first time running
                if process.start_time is None:
                    process.start_time = self.clock
                    
                # Generate new CPU burst for this process if needed
                if process.current_burst <= 0:
                    # Randomly generate burst between 3-15 time units based on process type
                    if "io_bound" in process.name:
                        process.current_burst = random.randint(2, 6)  # IO-bound: shorter bursts
                    elif "cpu_bound" in process.name:
                        process.current_burst = random.randint(8, 15)  # CPU-bound: longer bursts
                    elif "short" in process.name:
                        process.current_burst = random.randint(1, 4)  # Short tasks: very short bursts
                    else:
                        process.current_burst = random.randint(3, 10)  # Default
                        
                # Reset the slice counter for this run
                process.current_slice = 0
                
                print(f"[Clock:{self.clock}] Running process {pid} ({process.name}), priority:{process.priority}, "
                      f"steps:{process.executed_steps}, burst:{process.current_burst}")
                
            self.running_process = process
            self.last_running_pid = pid
            
            # Execute process for a time slice or until yield/completion
            run_completed = False
            process.current_slice += self.time_slice
            process.current_burst -= self.time_slice
            
            # Check if we should yield control based on time slice, burst completion, or quantum
            need_to_yield = False
            
            # For Round Robin, check if quantum is used up
            if self.scheduler_type == "round_robin":
                process.quantum_remaining -= self.time_slice
                if process.quantum_remaining <= 0:
                    need_to_yield = True
            
            # If burst is complete, we need to yield
            if process.current_burst <= 0:
                need_to_yield = True
            
            try:
                if need_to_yield:
                    # We've used up our time slice or quantum, yield control
                    # Record this execution segment
                    self.execution_log.append((self.clock, pid, process.name))
                    if process.current_run_start is not None:
                        process.run_history.append((process.current_run_start, self.clock))
                        process.current_run_start = None
                    
                    # For CPU bursts that complete, advance to next step of process
                    if process.current_burst <= 0:
                        start_time_cpu = time.time()
                        next_value = next(process.generator)
                        process_cpu_time = time.time() - start_time_cpu
                        process.cpu_time += process_cpu_time
                        process.executed_steps += 1
                        process.current_burst = 0  # Will generate new burst on next run
                        
                        # Handle yield value
                        if next_value is not None:
                            print(f"[Clock:{self.clock}] Process {pid} yielded: {next_value}")
                    
                    # Set process state back to ready
                    process.state = "ready"
                    
                    # For Round Robin, reset quantum if used up and requeue
                    if self.scheduler_type == "round_robin" and process.quantum_remaining <= 0:
                        process.quantum_remaining = self.time_quantum
                        print(f"[Clock:{self.clock}] Process {pid} quantum expired, requeuing")
                        
                        # Move to the end of ready queue for Round Robin
                        if pid in self.ready_queue:
                            self.ready_queue.remove(pid)
                        self.ready_queue.append(pid)
                    
                    run_completed = True
                
            except StopIteration as e:
                # Process completed
                process.state = "terminated"
                process.end_time = self.clock
                process.turnaround_time = process.end_time - process.arrival_time
                
                # Record final execution segment
                if process.current_run_start is not None:
                    process.run_history.append((process.current_run_start, self.clock))
                
                # Record return value
                if e.value is not None:
                    process.return_value = e.value
                    print(f"[Clock:{self.clock}] Process {pid} terminated with return value: {e.value}")
                else:
                    print(f"[Clock:{self.clock}] Process {pid} terminated")
                
                # Record termination to execution log
                self.execution_log.append((self.clock, pid, f"{process.name} (terminated)"))
                
                # Remove from ready queue
                if pid in self.ready_queue:
                    self.ready_queue.remove(pid)
                
                # Reset last running pid if this was the process
                if self.last_running_pid == pid:
                    self.last_running_pid = None
                
                # Move to terminated processes
                self.terminated_processes.append(process)
                del self.processes[pid]
                
                run_completed = True
            
            # Update system clock if run completed or time slice used
            if run_completed or process.current_slice >= self.time_slice:
                self.clock += self.time_slice
                self.running_process = None
                
                # Show status every 20 clock ticks
                if self.clock % 20 == 0:
                    print(f"\n[System status Clock:{self.clock}]")
                    self._print_process_status()
                    print("-" * 50)
            
        print("=" * 50)
        print(f"All processes completed. Total clock cycles: {self.clock}")
        print(f"Context switches: {self.context_switches}")
        
        # Print process statistics
        self._print_statistics()
        
        # If visualization enabled, show gantt chart
        if self.visualize:
            self._show_gantt_chart()

    def _scheduler(self) -> int:
        """Select next process based on scheduling algorithm"""
        if not self.processes:
            return None
            
        if self.scheduler_type == "fcfs":
            return self._fcfs_scheduler()
        elif self.scheduler_type == "sjf":
            return self._sjf_scheduler()
        elif self.scheduler_type == "priority":
            return self._priority_scheduler()
        elif self.scheduler_type == "round_robin":
            return self._round_robin_scheduler()
        else:
            # Default to FCFS
            return self._fcfs_scheduler()
            
    def _fcfs_scheduler(self) -> int:
        """First-Come, First-Served scheduling algorithm"""
        # Return the first process in the ready queue
        if self.ready_queue:
            return self.ready_queue[0]
        return None
        
    def _sjf_scheduler(self) -> int:
        """Shortest Job First scheduling algorithm"""
        # Select ready process with shortest estimated burst time
        shortest_time = float('inf')
        selected_pid = None
        
        for pid in self.ready_queue:
            process = self.processes[pid]
            if process.state == "ready" and process.estimated_burst_time < shortest_time:
                shortest_time = process.estimated_burst_time
                selected_pid = pid
                
        return selected_pid
        
    def _priority_scheduler(self) -> int:
        """Priority scheduling algorithm"""
        # Select ready process with highest priority (lowest number)
        highest_priority = float('inf')
        selected_pid = None
        
        for pid in self.ready_queue:
            process = self.processes[pid]
            if process.state == "ready" and process.priority < highest_priority:
                highest_priority = process.priority
                selected_pid = pid
                
        return selected_pid
        
    def _round_robin_scheduler(self) -> int:
        """Round Robin scheduling algorithm"""
        # Simply return the first process in the queue
        if self.ready_queue:
            return self.ready_queue[0]
        return None
        
    def _update_waiting_times(self, current_pid):
        """Update waiting time for all ready processes except the one about to run"""
        for pid, process in self.processes.items():
            if process.state == "ready" and pid != current_pid:
                process.waiting_time += self.time_slice
                
    def _print_process_status(self):
        """Print current status of all processes"""
        print(f"{'PID':<5} {'Name':<15} {'State':<10} {'Priority':<8} {'Steps':<8} {'Wait Time':<8} {'Burst':<8}")
        print("-" * 65)
        
        for pid, proc in self.processes.items():
            print(f"{pid:<5} {proc.name:<15} {proc.state:<10} {proc.priority:<8} "
                  f"{proc.executed_steps:<8} {proc.waiting_time:<8} {proc.current_burst:<8}")
        
    def _print_statistics(self):
        """Print statistics for all terminated processes"""
        print("\nProcess Statistics:")
        print("=" * 85)
        print(f"{'PID':<5} {'Name':<15} {'CPU Time':<10} {'Turnaround':<10} {'Wait Time':<10} "
              f"{'Priority':<8} {'Steps':<8} {'Return Value'}")
        print("-" * 85)
        
        avg_turnaround = 0
        avg_waiting = 0
        
        for proc in self.terminated_processes:
            print(f"{proc.pid:<5} {proc.name:<15} {proc.cpu_time:.4f}s    {proc.turnaround_time:<10} "
                  f"{proc.waiting_time:<10} {proc.priority:<8} {proc.executed_steps:<8} {proc.return_value}")
            avg_turnaround += proc.turnaround_time
            avg_waiting += proc.waiting_time
            
        if self.terminated_processes:
            avg_turnaround /= len(self.terminated_processes)
            avg_waiting /= len(self.terminated_processes)
            
        print("-" * 85)
        print(f"Average turnaround time: {avg_turnaround:.2f} clock cycles")
        print(f"Average waiting time: {avg_waiting:.2f} clock cycles")
        print(f"Total context switches: {self.context_switches}")
        
    def _show_gantt_chart(self):
        """Show Gantt chart to visualize process execution"""
        try:
            import matplotlib.pyplot as plt
            import numpy as np
            from matplotlib.patches import Rectangle
            
            fig, ax = plt.subplots(figsize=(14, 7))
            
            # Assign a color for each process
            process_colors = {}
            cmap = plt.cm.get_cmap('tab10', len(self.terminated_processes) + 1)
            
            for i, proc in enumerate(self.terminated_processes):
                process_colors[proc.pid] = cmap(i)
                
            # Draw execution segments for each process
            y_positions = {}
            current_y = 0
            
            for proc in sorted(self.terminated_processes, key=lambda p: p.pid):
                y_positions[proc.pid] = current_y
                current_y += 1
                
                for start, end in proc.run_history:
                    # Only draw segments with actual duration
                    if end > start:
                        ax.add_patch(Rectangle((start, y_positions[proc.pid]), 
                                              end - start, 0.8, 
                                              color=process_colors[proc.pid],
                                              alpha=0.7))
            
            # Set chart properties
            ax.set_xlim(0, self.clock)
            ax.set_ylim(-0.5, len(self.terminated_processes) - 0.5)
            ax.set_yticks([y_positions[p.pid] for p in self.terminated_processes])
            ax.set_yticklabels([f"P{p.pid}: {p.name}" for p in self.terminated_processes])
            ax.set_xlabel('Clock Cycles')
            ax.set_title(f'Process Execution Gantt Chart ({self.scheduler_type.upper()})')
            ax.grid(True, axis='x', linestyle='--', alpha=0.7)
            
            # Add vertical lines for context switches
            context_times = []
            for i in range(1, len(self.execution_log)):
                prev_time, prev_pid, _ = self.execution_log[i-1]
                curr_time, curr_pid, _ = self.execution_log[i]
                if prev_pid != curr_pid:
                    context_times.append(curr_time)
                    
            for switch_time in context_times:
                ax.axvline(x=switch_time, color='red', linestyle='--', alpha=0.3)
            
            # Add legend
            legend_patches = [plt.Rectangle((0,0), 1, 1, color=process_colors[p.pid]) 
                             for p in self.terminated_processes]
            legend_patches.append(plt.Line2D([0], [0], color='red', linestyle='--', alpha=0.7))
            
            legend_labels = [f"P{p.pid} (priority:{p.priority})" for p in self.terminated_processes]
            legend_labels.append("Context Switch")
            
            ax.legend(legend_patches, legend_labels,
                     loc='upper center', bbox_to_anchor=(0.5, -0.1), ncol=min(4, len(legend_labels)))
            
            plt.tight_layout()
            
            # Save chart
            plt.savefig(f"gantt_chart_{self.scheduler_type}.png", bbox_inches='tight')
            print(f"\nGantt chart saved as gantt_chart_{self.scheduler_type}.png")
            
            # Show chart
            plt.show()
            
        except ImportError:
            print("\nWarning: Cannot generate Gantt chart, please install matplotlib")
        except Exception as e:
            print(f"\nError generating Gantt chart: {e}")

def main():
    """OS main entry point"""
    parser = argparse.ArgumentParser(description='Simple OS simulator with multiple scheduling algorithms')
    parser.add_argument('programs', nargs='+', help='Python program files to run')
    parser.add_argument('-s', '--scheduler', choices=['fcfs', 'sjf', 'priority', 'round_robin'],
                      default='fcfs', help='Select scheduling algorithm (default: fcfs)')
    parser.add_argument('-q', '--quantum', type=int, default=5, 
                      help='Time quantum size for Round Robin (default: 5)')
    parser.add_argument('-t', '--time-slice', type=int, default=1,
                      help='Time slice granularity (default: 1)')
    parser.add_argument('-v', '--visualize', action='store_true',
                      help='Show Gantt chart after completion')
    parser.add_argument('-p', '--priorities', type=int, nargs='+',
                      help='Specify priorities for each program (lower number = higher priority)')
    
    args = parser.parse_args()
    
    # Initialize OS
    os_system = SimpleOS(scheduler_type=args.scheduler, 
                        time_quantum=args.quantum,
                        time_slice=args.time_slice, 
                        visualize=args.visualize)
    
    # Load all specified programs
    for i, program in enumerate(args.programs):
        priority = args.priorities[i] if args.priorities and i < len(args.priorities) else None
        os_system.load_program(program, priority)
    
    # Run OS
    os_system.run()

if __name__ == "__main__":
    main()