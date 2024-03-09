import multiprocessing
import threading
import time
import numpy as np
from multiprocessing import shared_memory, Process, Queue as ProcessQueue
from queue import Queue
from threading import Thread

# ----- Process-Based IPC with Shared Memory -----
def modify_shared_memory(name, shape, dtype):
    existing_shm = shared_memory.SharedMemory(name=name)
    np_array = np.ndarray(shape, dtype=dtype, buffer=existing_shm.buf)
    np_array += 1  # Modify the shared array
    existing_shm.close()

def run_process_shared_memory():
    arr = np.zeros(10)
    shm = shared_memory.SharedMemory(create=True, size=arr.nbytes)
    np_array_original = np.ndarray(arr.shape, dtype=arr.dtype, buffer=shm.buf)
    np.copyto(np_array_original, arr)
    p = Process(target=modify_shared_memory, args=(shm.name, arr.shape, arr.dtype))
    p.start()
    p.join()
    print(np_array_original)
    shm.unlink()  # Clean up shared memory

# ----- Process-Based IPC with Message Passing -----
def sender(queue):
    for i in range(10):
        queue.put(f"Message {i}")

def receiver(queue):
    while True:
        message = queue.get()
        if message == "END":
            break
        print(f"Received: {message}")

def run_process_message_passing():
    queue = ProcessQueue()
    p1 = Process(target=sender, args=(queue,))
    p2 = Process(target=receiver, args=(queue,))
    p1.start()
    p2.start()
    p1.join()
    queue.put("END")
    p2.join()

# ----- Thread-Based IPC with Shared Memory -----
shared_data = []

def thread_function(name):
    for i in range(5):
        shared_data.append(f"Data from {name}: {i}")
        time.sleep(1)

def run_thread_shared_memory():
    threads = []
    for index in range(2):
        x = Thread(target=thread_function, args=(f"Thread-{index}",))
        threads.append(x)
        x.start()

    for index, thread in enumerate(threads):
        thread.join()
    print(shared_data)

# ----- Thread-Based IPC with Message Passing -----
def thread_producer(queue):
    for i in range(10):
        queue.put(f"Message {i}")

def thread_consumer(queue):
    while True:
        message = queue.get()
        if message == "END":
            break
        print(f"Received: {message}")

def run_thread_message_passing():
    queue = Queue()
    t1 = Thread(target=thread_producer, args=(queue,))
    t2 = Thread(target=thread_consumer, args=(queue,))
    t1.start()
    t2.start()
    t1.join()
    queue.put("END")
    t2.join()

if __name__ == "__main__":
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
