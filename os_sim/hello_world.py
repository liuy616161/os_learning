def main():
    """A simple example program that uses yield for cooperative multitasking"""
    print("Hello from process!")
    yield "Step 1 completed"
    
    # 模拟一些计算
    result = 0
    for i in range(10):
        result += i
        yield f"Calculating: {result}"
    
    print("World from process!")
    yield "Step 2 completed"
    
    # 返回最终结果
    return f"Final result: {result}"