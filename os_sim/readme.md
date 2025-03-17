# Python简易操作系统调度器

这是一个用Python实现的简易操作系统调度器模拟器，主要用于教学和演示不同进程调度算法的工作原理和性能差异。

## 功能特点

- 支持多种经典调度算法：
  - 先来先服务 (FCFS)
  - 最短作业优先 (SJF)
  - 优先级调度
  - 时间片轮转 (Round Robin)
- 提供进程执行的可视化 (甘特图)
- 收集和展示各种性能指标
- 使用Python生成器实现协作式多任务

## 安装要求

- Python 3.6+
- matplotlib (用于可视化)
  - 安装：`pip install matplotlib`

## 使用方法

### 基本运行

```bash
python os_system.py <程序文件> [程序文件2 ...] [选项]
```

### 命令行选项

- `-s, --scheduler`: 选择调度算法 (fcfs, sjf, priority, round_robin)
- `-q, --quantum`: 设置时间片大小 (用于Round Robin算法)
- `-v, --visualize`: 运行结束后显示甘特图
- `-p, --priorities`: 为程序指定优先级 (数字越小优先级越高)

### 示例

```bash
# 使用FCFS算法运行两个程序
python os_system.py cpu_bound.py io_bound.py -s fcfs

# 使用时间片轮转算法，时间片为3
python os_system.py cpu_bound.py io_bound.py short_task.py -s round_robin -q 3

# 使用优先级调度，并指定优先级
python os_system.py high_priority_task.py cpu_bound.py -s priority -p 1 5

# 运行后显示甘特图
python os_system.py cpu_bound.py io_bound.py -s fcfs -v
```

## 示例程序

系统自带几个示例程序：

- `cpu_bound.py`: 模拟CPU密集型计算
- `io_bound.py`: 模拟IO密集型操作
- `short_task.py`: 模拟短时任务
- `high_priority_task.py`: 模拟高优先级任务

## 编写自己的程序

您可以创建自己的程序来测试调度器。每个程序需要：

1. 定义一个`main()`函数作为入口点
2. `main()`函数必须是一个生成器函数（包含`yield`语句）
3. 使用`yield`语句主动让出CPU控制权
4. 可以通过`return`语句返回最终结果

示例：
```python
def main():
    """自定义程序示例"""
    print("开始执行")
    
    for i in range(5):
        # 执行一些操作
        result = i * 10
        # 让出CPU控制权
        yield f"计算结果: {result}"
    
    print("执行完成")
    return "最终结果"
```

## 学习建议

1. 尝试不同的调度算法运行相同的程序集
2. 比较各算法的平均周转时间、等待时间和上下文切换次数
3. 观察甘特图中的执行顺序和时间分配
4. 思考各算法在不同场景下的适用性

## 扩展和修改

您可以扩展这个系统以:
1. 实现更多调度算法
2. 添加进程间通信机制
3. 模拟内存管理
4. 实现I/O设备管理

## 许可

MIT许可证