def main():
    """IO-bound process simulation"""
    print("Starting IO-intensive task")
    
    for i in range(1, 6):
        # Simulate IO operation
        print(f"IO operation {i}/5 in progress...")
        # Yield CPU to simulate waiting for IO
        yield f"IO waiting {i}"
        
        # Do minimal computation
        result = i * 2
        yield f"IO result processing: {result}"
    
    print("IO-intensive task completed")
    return "IO task completed, data processed"