def main():
    """High-priority task simulation"""
    print("Starting high-priority task")
    
    # Medium-length task with high priority
    for i in range(5):
        yield f"High-priority operation {i+1}/5"
    
    print("High-priority task completed")
    return "Urgent task processed"