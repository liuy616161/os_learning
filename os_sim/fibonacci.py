def main():
    """计算斐波那契数列的程序"""
    print("开始计算斐波那契数列")
    
    n = 100  # 计算前10个斐波那契数
    fib_sequence = [0, 1]
    
    yield "初始化完成"
    
    for i in range(2, n):
        next_fib = fib_sequence[i-1] + fib_sequence[i-2]
        fib_sequence.append(next_fib)
        yield f"F({i}) = {next_fib}"
    
    print(f"斐波那契数列 (前{n}个): {fib_sequence}")
    return fib_sequence