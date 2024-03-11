import multiprocessing
import threading
import time
import numpy as np
from multiprocessing import shared_memory, Process, Queue as ProcessQueue
from queue import Queue
from threading import Thread

# ----- Process-Based IPC (Inter-Process Communication) with Shared Memory -----
def modify_shared_memory(name, shape, dtype):
    # Access existing shared memory
    existing_shm = shared_memory.SharedMemory(name=name)
    # Create a NumPy array that uses the buffer of the shared memory
    np_array = np.ndarray(shape, dtype=dtype, buffer=existing_shm.buf)
    np_array += 1  # Increment each element in the shared array by 1
    existing_shm.close()  # Close the shared memory object

def run_process_shared_memory():
    arr = np.zeros(10)  # Initialize a numpy array of zeros
    # Create a new shared memory block
    shm = shared_memory.SharedMemory(create=True, size=arr.nbytes)
    # Create a numpy array that uses the buffer of the shared memory
    np_array_original = np.ndarray(arr.shape, dtype=arr.dtype, buffer=shm.buf)
    np.copyto(np_array_original, arr)  # Copy data to the shared memory array
    # Start a new process that will modify the shared memory
    p = Process(target=modify_shared_memory, args=(shm.name, arr.shape, arr.dtype))
    p.start()
    p.join()  # Wait for the process to finish
    print(np_array_original)  # Print the modified array
    shm.unlink()  # Remove the shared memory block

# ----- Process-Based IPC with Message Passing -----
def sender(queue):
    for i in range(10):
        queue.put(f"Message {i}")  # Send messages through the queue

def receiver(queue):
    while True:
        message = queue.get()  # Receive a message from the queue
        if message == "END":
            break
        print(f"Received: {message}")

def run_process_message_passing():
    queue = ProcessQueue()  # Create a multiprocessing queue
    p1 = Process(target=sender, args=(queue,))
    p2 = Process(target=receiver, args=(queue,))
    p1.start()
    p2.start()
    p1.join()  # Wait for sender to finish
    queue.put("END")  # Send a termination message
    p2.join()  # Wait for receiver to finish

# ----- Thread-Based IPC with Shared Memory -----
shared_data = []  # Shared list used by threads

def thread_function(name):
    for i in range(5):
        shared_data.append(f"Data from {name}: {i}")  # Append data to the shared list
        time.sleep(1)  # Simulate work by sleeping

def run_thread_shared_memory():
    threads = []
    for index in range(2):
        x = Thread(target=thread_function, args=(f"Thread-{index}",))
        threads.append(x)
        x.start()

    for thread in threads:
        thread.join()  # Wait for all threads to finish
    print(shared_data)  # Print the shared data

# ----- Thread-Based IPC with Message Passing -----
def thread_producer(queue):
    for i in range(10):
        queue.put(f"Message {i}")  # Send messages through the queue

def thread_consumer(queue):
    while True:
        message = queue.get()  # Receive a message from the queue
        if message == "END":
            break
        print(f"Received: {message}")

def run_thread_message_passing():
    queue = Queue()  # Create a threading queue
    t1 = Thread(target=thread_producer, args=(queue,))
    t2 = Thread(target=thread_consumer, args=(queue,))
    t1.start()
    t2.start()
    t1.join()  # Wait for producer to finish
    queue.put("END")  # Send a termination message
    t2.join()  # Wait for consumer to finish

if __name__ == "__main__":
    # Measure and print the execution time for each IPC mechanism
    start_time = time.perf_counter()
    print("Process-Based IPC with Shared Memory")
    run_process_shared_memory()
    print("Elapsed time:", time.perf_counter() - start_time, "seconds\n")

    start_time = time.perf_counter()
    print("Process-Based IPC with Message Passing")
    run_process_message_passing()
    print("Elapsed time:", time.perf_counter() - start_time, "seconds\n")

    start_time = time.perf_counter()
    print("Thread-Based IPC with Shared Memory")
    run_thread_shared_memory()
    print("Elapsed time:", time.perf_counter() - start_time, "seconds\n")

    start_time = time.perf_counter()
    print("Thread-Based IPC with Message Passing")
    run_thread_message_passing()
    print("Elapsed time:", time.perf_counter() - start_time, "seconds")
