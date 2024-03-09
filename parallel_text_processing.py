import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import time  # Import time module for performance measurement
import psutil

def process_segment(start, end, file_path):
    """Process a file segment to convert to uppercase and count characters."""
    counts = {}
    with open(file_path, 'r', encoding='utf-8') as file:
        file.seek(start)
        text = file.read(end - start)
        text = text.upper()
        for char in text:
            if char.isalpha():
                counts[char] = counts.get(char, 0) + 1
    return counts

def merge_counts(counts_list):
    """Merge character counts from all segments."""
    final_counts = {}
    for counts in counts_list:
        for char, count in counts.items():
            final_counts[char] = final_counts.get(char, 0) + count
    return final_counts

def main(file_path):
    # Start timing and resource monitoring
    start_time = time.time_ns()
    process = psutil.Process()  # Get current Python process
    initial_cpu = process.cpu_percent(interval=None)
    initial_memory = process.memory_info().rss  # Resident Set Size: physical memory used

    # Existing code for processing
    file_size = os.path.getsize(file_path)
    num_workers = 4  # Adjust based on your system's capabilities
    chunk_size = file_size // num_workers
    futures = []

    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        for i in range(num_workers):
            start = i * chunk_size
            end = start + chunk_size if i < num_workers - 1 else file_size
            futures.append(executor.submit(process_segment, start, end, file_path))

        results = [future.result() for future in as_completed(futures)]

    final_counts = merge_counts(results)

    print(final_counts)

    # End timing and resource monitoring
    end_time = time.time_ns()
    final_cpu = process.cpu_percent(interval=None)
    final_memory = process.memory_info().rss
    cpu_usage = final_cpu - initial_cpu
    memory_usage = final_memory - initial_memory  # This is a simplistic approach

    print(f"Processing completed in {end_time - start_time:.2f} nano seconds.")
    print(f"CPU usage change: {cpu_usage}%")
    print(f"Memory usage increase: {memory_usage / (1024**2):.2f} MB")  # Convert bytes to MB

# Testing different text sizes
#main('BeeMovie.txt')
#main('Frankenstein.txt')
main('Dracula.txt')