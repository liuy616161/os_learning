#!/usr/bin/env python3
import sys
import importlib.util
import time
from typing import Dict, List, Generator, Any, Tuple

class Process:
    """表示操作系统中的一个进程"""
    def __init__(self, pid: int, name: str, generator: Generator, priority: int = 1):
        self.pid = pid
        self.name = name
        self.generator = generator  # 使用generator进行协作式多任务处理
        self.state = "ready"  # ready, running, waiting, terminated
        self.priority = priority
        self.start_time = time.time()
        self.end_time = None
        self.cpu_time = 0
        self.last_run = 0
        self.return_value = None

    def __str__(self):
        return f"Process(pid={self.pid}, name={self.name}, state={self.state})"

class SimpleOS:
    """简单的操作系统模拟实现"""
    def __init__(self):
        self.processes: Dict[int, Process] = {}
        self.current_pid = 0
        self.running_process = None
        self.clock = 0
        self.terminated_processes: List[Process] = []

    def load_program(self, file_path: str) -> int:
        """加载一个Python程序作为进程"""
        try:
            # 从文件路径中提取模块名
            module_name = file_path.split('/')[-1]
            if module_name.endswith('.py'):
                module_name = module_name[:-3]
            
            # 加载Python模块
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            if spec is None or spec.loader is None:
                print(f"Error: Could not load {file_path}")
                return -1
                
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # 检查模块是否有main函数
            if not hasattr(module, 'main') or not callable(module.main):
                print(f"Error: {file_path} does not have a main() function")
                return -1
            
            # 创建进程
            pid = self._create_process(module_name, module.main())
            print(f"Process {pid} ({module_name}) loaded successfully")
            return pid
        except Exception as e:
            print(f"Error loading program: {e}")
            return -1

    def _create_process(self, name: str, generator: Generator) -> int:
        """创建一个新进程"""
        self.current_pid += 1
        process = Process(self.current_pid, name, generator)
        self.processes[self.current_pid] = process
        return self.current_pid

    def run(self):
        """运行操作系统调度器"""
        print("Starting SimpleOS...")
        print("=" * 40)

        # 进程调度循环
        while self.processes:
            # 选择下一个要运行的进程
            pid = self._scheduler()
            if pid is None:
                break
                
            process = self.processes[pid]
            process.state = "running"
            self.running_process = process
            
            print(f"Running process {pid} ({process.name})")
            
            try:
                # 执行进程的一个步骤
                start_time = time.time()
                next_value = next(process.generator)
                process.cpu_time += time.time() - start_time
                process.last_run = self.clock
                
                # 处理yield返回的值
                if next_value is not None:
                    print(f"Process {pid} yielded: {next_value}")
                
                # 将进程状态设置为就绪
                process.state = "ready"
            except StopIteration as e:
                # 进程执行完成
                process.state = "terminated"
                process.end_time = time.time()
                if e.value is not None:
                    process.return_value = e.value
                    print(f"Process {pid} terminated with return value: {e.value}")
                else:
                    print(f"Process {pid} terminated")
                
                # 移除已终止的进程
                self.terminated_processes.append(process)
                del self.processes[pid]
            
            # 更新系统时钟
            self.clock += 1
            
        print("=" * 40)
        print("All processes completed.")
        self._print_statistics()

    def _scheduler(self) -> int:
        """简单的轮转调度算法"""
        if not self.processes:
            return None
            
        # 简单地选择第一个就绪状态的进程
        for pid, process in self.processes.items():
            if process.state == "ready":
                return pid
                
        return None
        
    def _print_statistics(self):
        """打印所有已终止进程的统计信息"""
        print("\nProcess Statistics:")
        print("=" * 60)
        print(f"{'PID':<5} {'Name':<15} {'CPU Time':<10} {'Wall Time':<10} {'Return Value'}")
        print("-" * 60)
        
        for proc in self.terminated_processes:
            wall_time = proc.end_time - proc.start_time
            print(f"{proc.pid:<5} {proc.name:<15} {proc.cpu_time:.4f}s    {wall_time:.4f}s    {proc.return_value}")

def main():
    """操作系统主入口"""
    if len(sys.argv) < 2:
        print("Usage: ./os_system.py <program.py> [program2.py ...]")
        sys.exit(1)
    
    # 初始化操作系统
    os = SimpleOS()
    
    # 加载所有指定的程序
    for program in sys.argv[1:]:
        os.load_program(program)
    
    # 运行操作系统
    os.run()

if __name__ == "__main__":
    main()