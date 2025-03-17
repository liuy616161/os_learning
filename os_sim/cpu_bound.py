def main():
    """CPU-bound process simulation"""
    print("Starting CPU-intensive calculation")
    
    # This process has longer execution time
    result = 0
    for i in range(1, 8):
        # Simulate heavy computation
        for j in range(i * 1000):
            result += j % 10
            
        # Must periodically yield CPU for cooperative multitasking
        yield f"Calculation progress: {i*15}%, current result: {result}"
    
    print(f"CPU-intensive calculation completed, final result: {result}")
    return result