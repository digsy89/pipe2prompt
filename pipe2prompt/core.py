def run_task(filename: str):
    """Example function to process a file."""
    try:
        with open(filename, 'r') as f:
            data = f.read()
        print(f"Processing {len(data)} characters from {filename}")
    except FileNotFoundError:
        print(f"Error: {filename} not found.")
