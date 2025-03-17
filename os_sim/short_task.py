def main():
    """Short task process simulation"""
    print("Starting short task")
    
    # Only performs minimal work
    result = 0
    for i in range(3):
        result += i
        yield f"Short task progress: {(i+1)/3*100}%"
    
    print("Short task completed")
    return "Short task result: " + str(result)