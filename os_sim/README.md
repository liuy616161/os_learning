# 操作系统调度算法模拟器

这个项目是一个用Python实现的操作系统进程调度模拟器，主要用于教学演示不同调度算法的工作原理和性能特点。通过可视化和详细的统计信息，帮助学生更好地理解操作系统调度算法的行为。

## 功能特点

- **多种调度算法支持**：
  - 先来先服务 (FCFS)
  - 最短作业优先 (SJF)
  - 优先级调度 (Priority)
  - 时间片轮转 (Round Robin)
  - 最短剩余时间优先 (SRTF)
  - 多级反馈队列 (MLFQ)
  - 最早截止时间优先 (EDF)
  - 公平共享调度 (Fair Share)

- **可视化功能**：
  - 生成甘特图展示进程执行序列
  - 上下文切换标记
  - 进程运行状态实时显示

- **统计指标**：
  - 周转时间统计
  - 等待时间统计
  - CPU使用时间统计
  - 上下文切换次数统计

- **灵活配置**：
  - 可自定义时间片大小
  - 可指定进程优先级
  - 可调整时间粒度

## 安装要求

- Python 3.6+
- matplotlib (用于甘特图可视化)
  ```bash
  pip install matplotlib
  ```

## 使用方法

### 基本用法

### 基本用法

```bash
python os_system.py [程序文件...] [选项]
```

### 命令行参数

- `-s, --scheduler`: 选择调度算法 (fcfs, sjf, priority, round_robin, srtf, mlfq, edf, fair)
- `-q, --quantum`: 时间片大小，用于Round Robin调度 (默认: 5)
- `-t, --time-slice`: 时间粒度 (默认: 1)
- `-v, --visualize`: 运行结束后显示甘特图
- `-p, --priorities`: 为每个程序指定优先级（数字越小优先级越高）

### 使用示例

**1. 使用先来先服务 (FCFS) 调度算法运行多个程序**

```bash
python os_system.py cpu_bound.py io_bound.py short_task.py -s fcfs -v
```

**2. 使用最短作业优先 (SJF) 调度算法**

```bash
python os_system.py cpu_bound.py io_bound.py short_task.py -s sjf -v
```

**3. 使用优先级调度，并指定每个进程的优先级**

```bash
python os_system.py high_priority_task.py cpu_bound.py io_bound.py -s priority -p 1 5 10 -v
```

**4. 使用时间片轮转 (Round Robin) 调度，指定时间片大小**

```bash
python os_system.py cpu_bound.py io_bound.py -s round_robin -q 3 -v
```

**5. 使用最短剩余时间优先 (SRTF) 调度算法**

```bash
python os_system.py cpu_bound.py short_task.py io_bound.py -s srtf -v
```

**6. 使用多级反馈队列 (MLFQ) 调度**

```bash
python os_system.py cpu_bound.py io_bound.py short_task.py -s mlfq -v
```

## 编写自己的进程程序

您可以创建自己的Python程序作为进程，格式要求如下：

1. 必须包含一个`main()`函数作为入口点
2. `main()`函数必须是一个生成器函数（包含`yield`语句）
3. 可以使用`yield`语句报告中间状态
4. 可以使用`return`语句返回最终结果

示例进程程序：

```python
def main():
    """示例进程"""
    print("进程开始执行")
    
    # 执行一些任务
    for i in range(1, 4):
        result = i * 10
        # 使用yield报告状态并让出CPU
        yield f"完成步骤 {i}/3，结果: {result}"
    
    print("进程执行完毕")
    # 返回最终结果
    return "处理完成，最终结果"
```

## 内置进程示例

本模拟器附带几个示例进程程序：

1. **cpu_bound.py**: 模拟CPU密集型进程，需要大量计算
2. **io_bound.py**: 模拟IO密集型进程，频繁等待IO操作
3. **short_task.py**: 模拟短时进程，执行时间短
4. **high_priority_task.py**: 模拟高优先级任务，适合优先级调度测试

## 实验设计示例

### 实验1: 比较FCFS与SJF对短进程的处理

目的：观察短进程在不同调度算法下的等待时间差异

```bash
# 先来先服务 (FCFS)
python os_system.py cpu_bound.py short_task.py -s fcfs -v

# 最短作业优先 (SJF)
python os_system.py cpu_bound.py short_task.py -s sjf -v
```

预期结果：在FCFS中，如果cpu_bound.py先到达，short_task.py将需要等待较长时间；而在SJF中，short_task.py将先执行，减少等待时间。

### 实验2: 观察Round Robin时间片大小的影响

目的：了解时间片大小对上下文切换和响应时间的影响

```bash
# 小时间片 (2个时间单位)
python os_system.py cpu_bound.py io_bound.py -s round_robin -q 2 -v

# 中等时间片 (5个时间单位)
python os_system.py cpu_bound.py io_bound.py -s round_robin -q 5 -v

# 大时间片 (10个时间单位)
python os_system.py cpu_bound.py io_bound.py -s round_robin -q 10 -v
```

预期结果：较小的时间片会导致更多的上下文切换但提供更好的响应时间，较大的时间片则减少上下文切换但响应时间变长。

## 理解模拟结果

### 甘特图解读

甘特图显示了每个进程的执行时间段：
- 横轴表示时间（时钟周期）
- 纵轴表示不同的进程
- 彩色块表示进程执行时间段
- 红色虚线表示上下文切换点

### 性能指标解读

- **周转时间**：进程从创建到完成的总时间
- **等待时间**：进程在就绪队列中等待的总时间
- **上下文切换次数**：进程切换的总次数（反映调度开销）

## 进阶使用

### 调整时间粒度

时间粒度（time slice）决定了模拟的精细程度：

```bash
# 使用更细的时间粒度 (0.5个单位)
python os_system.py cpu_bound.py io_bound.py -s priority -t 0.5 -v
```

### 结合多种进程类型

通过组合不同类型的进程，可以创建更复杂的场景：

```bash
# 混合多种进程类型
python os_system.py cpu_bound.py io_bound.py short_task.py high_priority_task.py -s mlfq -v
```

## 常见问题

### Q: 为什么某些调度算法下进程不按预期顺序运行？
A: 检查进程的估计执行时间、优先级设置，以及调度算法的实现细节。特别是SJF和SRTF依赖于预估的执行时间。

### Q: 为什么甘特图无法显示？
A: 确保已安装matplotlib库：`pip install matplotlib`

### Q: 如何比较不同调度算法的性能？
A: 使用相同的进程组合，运行不同的调度算法，然后比较平均等待时间、平均周转时间和上下文切换次数。

## 项目结构

- **os_system.py**: 主程序，实现调度器和系统模拟
- **cpu_bound.py**, **io_bound.py**, 等: 示例进程程序
- **操作系统调度算法详解.md**: 详细的调度算法说明文档
- **README.md**: 项目说明文件（本文档）

## 扩展与贡献

欢迎贡献新的调度算法实现或进程模型！可以通过以下方式扩展项目：

1. 实现新的调度算法
2. 添加更多类型的示例进程
3. 增强可视化和统计功能
4. 添加更多的教学实验

---

*本模拟器为教学目的开发，简化了真实操作系统的许多复杂性，仅用于演示基本调度原理。*