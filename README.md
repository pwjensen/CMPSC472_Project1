# Project Report

By: Paul Jensen

## Introduction

The primary objective of this project is to design and implement an advanced Process Manager that not only empowers users to create, manage, and synchronize processes but also offers a comprehensive set of features to facilitate robust inter-process communication (IPC) and synchronization between threads. This Process Manager is designed to provide a unified and user-friendly interface for process creation, management, and synchronization, harnessing the capabilities of system calls for process and thread control. It stands as an embodiment of ingenuity in the domain of multi-processing, striving to enhance the performance and stability of diverse applications.

**Objectives:**

To manipulate processes and threads.
To explore inter-process communication mechanisms, through memory sharing and message passing.
To process text files of varying sizes through use of parallelized operations
To evaluate the performance of different aspects of multiprocess/multithread functionality

## System Requirements

- Python

- psutil

- numpy

## Multi-Process and Thread Manager

### - Custom Process/Thread

```python
class CustomProcess:
    def __init__(self, name):
        self.name = name
        self.pause_event = ProcessEvent()
        self.pause_event.set()

    def run(self):
        logging.info(f"Process {self.name} started.")
        while True:
            self.pause_event.wait()
            time.sleep(1)  # Simulate work

class CustomThread:
    def __init__(self, name):
        self.name = name
        self.pause_event = threading.Event()
        self.pause_event.set()

    def run(self):
        logging.info(f"Thread {self.name} started.")
        while True:
            self.pause_event.wait()
            time.sleep(1)  # Simulate work
```

### - Process/Thread Management

`ProcessManager` Class:

- Manages custom processes by creating, pausing, resuming, listing, and terminating them. It keeps track of processes and their IDs, along with a mapping from custom names to process IDs.

`ThreadManager` Class:

- Manages custom threads similarly to `ProcessManager`, including creating, pausing, resuming, and listing threads. It tracks threads and their thread IDs (TIDs), and maps names to TIDs.

```python
class ProcessManager:
    def __init__(self):
        self.processes = {}
        self.names_to_pids = {}

    def create_process(self, name):
        if name in self.names_to_pids:
            logging.error(f"A process with the name '{name}' already exists.")
            return
        process = CustomProcess(name)
        p = Process(target=process.run)
        p.start()
        self.processes[p.pid] = {'process': p, 'pause_event': process.pause_event, 'name': name}
        self.names_to_pids[name] = p.pid
        logging.info(f"Process '{name}' with PID {p.pid} created.")

    def pause_process(self, identifier):
        pid = self.names_to_pids.get(identifier, identifier)
        if pid in self.processes:
            self.processes[pid]['pause_event'].clear()
            logging.info(f"Process '{self.processes[pid]['name']}' with PID {pid} paused.")
        else:
            logging.error(f"Process with identifier '{identifier}' not found.")

    def resume_process(self, identifier):
        pid = self.names_to_pids.get(identifier, identifier)
        if pid in self.processes:
            self.processes[pid]['pause_event'].set()
            logging.info(f"Process '{self.processes[pid]['name']}' with PID {pid} resumed.")
        else:
            logging.error(f"Process with identifier '{identifier}' not found.")

    def terminate_process(self, identifier):
        pid = self.names_to_pids.get(identifier, identifier)
        if pid in self.processes:
            name = self.processes[pid]['name']
            self.processes[pid]['process'].terminate()
            self.processes[pid]['process'].join()
            del self.processes[pid]
            del self.names_to_pids[name]
            logging.info(f"Process '{name}' with PID {pid} terminated.")
        else:
            logging.error(f"Process with identifier '{identifier}' not found.")

    def list_processes(self):
        logging.info("List of running processes:")
        for pid, process_info in self.processes.items():
            status = "Paused" if not process_info['pause_event'].is_set() else "Running"
            logging.info(f"PID: {pid}, Name: {process_info['name']}, Status: {status}")

class ThreadManager:
    def __init__(self):
        self.threads = {}
        self.names_to_tids = {}

    def create_thread(self, name):
        if name in self.names_to_tids:
            logging.error(f"A thread with the name '{name}' already exists.")
            return
        thread = CustomThread(name)
        t = threading.Thread(target=thread.run, name=name)
        t.start()
        self.threads[t.ident] = {'thread': t, 'pause_event': thread.pause_event, 'name': name}
        self.names_to_tids[name] = t.ident
        logging.info(f"Thread '{name}' with TID {t.ident} created.")

    def pause_thread(self, identifier):
        tid = self.names_to_tids.get(identifier, identifier)
        if tid in self.threads:
            self.threads[tid]['pause_event'].clear()
            logging.info(f"Thread '{self.threads[tid]['name']}' with TID {tid} paused.")
        else:
            logging.error(f"Thread with identifier '{identifier}' not found.")

    def resume_thread(self, identifier):
        tid = self.names_to_tids.get(identifier, identifier)
        if tid in self.threads:
            self.threads[tid]['pause_event'].set()
            logging.info(f"Thread '{self.threads[tid]['name']}' with TID {tid} resumed.")
        else:
            logging.error(f"Thread with identifier '{identifier}' not found.")

    def list_threads(self):
        logging.info("List of running threads:")
        for tid, thread_info in self.threads.items():
            status = "Paused" if not thread_info['pause_event'].is_set() else "Running"
            logging.info(f"TID: {tid}, Name: {thread_info['name']}, Status: {status}")

```

### CLI Management

`CLIManager` Class (Extends `threading.Thread`):

- Provides a command-line interface to interact with the process and thread managers. It processes commands from a queue to create, list, pause, resume, or terminate processes and threads based on user input.

- Inherits from `threading.Thread` to run the CLI in a separate thread, allowing it to listen for commands while the main thread continues execution.

```python
class CLIManager(threading.Thread):
    def __init__(self, process_manager, thread_manager):
        super().__init__()
        self.process_manager = process_manager
        self.thread_manager = thread_manager
        self.commands = queue.Queue()

    def run(self):
        while True:
            command = self.commands.get()
            if command[0] == "exit":
                logging.info("Exiting the Manager.")
                break
            self.execute_command(command)
            time.sleep(0.5)  # Give time for logging messages to be processed

    def execute_command(self, command):
        if len(command) < 2:
            logging.error("Invalid command. Please include the operation and type.")
            return

        operation, entity_type = command[0], command[1]

        if operation == "create" and len(command) >= 3:
            name = command[2]
            if entity_type == 'process':
                self.process_manager.create_process(name)
            elif entity_type == 'thread':
                self.thread_manager.create_thread(name)
        elif operation == "list":
            if entity_type == 'process':
                self.process_manager.list_processes()
            elif entity_type == 'thread':
                self.thread_manager.list_threads()
        elif len(command) >= 3:
            identifier = command[2]
            if entity_type == 'process':
                if operation == "pause":
                    self.process_manager.pause_process(identifier)
                elif operation == "resume":
                    self.process_manager.resume_process(identifier)
                elif operation == "terminate":
                    self.process_manager.terminate_process(identifier)
            elif entity_type == 'thread':
                if operation == "pause":
                    self.thread_manager.pause_thread(identifier)
                elif operation == "resume":
                    self.thread_manager.resume_thread(identifier)
                # No terminate operation for threads due to safety concerns

    def submit_command(self, command):
        self.commands.put(command)
```

### Main

- Initializes the process and thread managers, and the CLI manager.

- Starts the CLI manager thread.

- Enters a loop to accept commands from the user, splitting the input to interpret commands and their parameters (e.g., `create process MyProcess`).

- Submits commands to the CLI manager for execution and handles the special `exit` command to break the loop and terminate the program.

### Overview & Usage

This code effectively demonstrates advanced Python features like multiprocessing, multithreading, class inheritance, and event-driven programming to create a mini-framework for managing processes and threads through a simple CLI.

To interact with the command line interface, there are several options:
`create process/thread p1` - Creates a process and names it p1 (p1 can be anything)

`pause process/thread p1` - Pauses said process/thread

`resume process/thread p1` - Resumes said process/thread

`terminate process p1` - Terminates said process

`list process\thread` - Lists all processes/threads and if they are currently running or are paused

![Process Methods](/Images/processes.png)

![Thread Methods](/Images/threads.png)

## IPC

### Process-Based IPC with Shared Memory

Demonstrates how to share memory between processes using shared_memory. It creates a shared NumPy array that is modified by a child process.

`modify_shared_memory`: Modifies the shared NumPy array by incrementing its values.
`run_process_shared_memory`: Sets up shared memory, copies an initial array to it, spawns a process to modify the array, and cleans up the shared memory.

```python
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
```

![Process IPC Shared Memory](/Images/psharedmem.png)

### Process-Based IPC with Message Passing

Shows message passing between processes using a `ProcessQueue`. It implements a simple sender and receiver model.

`sender`: Puts a series of messages into the queue.

`receiver`: Retrieves messages from the queue and terminates on a special "END" message.

`run_process_message_passing`: Initializes the queue, starts sender and receiver processes, and ensures proper termination.

```python
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
```

![Process IPC Message Passing](/Images/pmesspass.png)

### Thread-Based IPC with Shared Memory

Illustrates thread-safe access to a shared Python list by multiple threads. Each thread appends data to the shared list.

`thread_function`: A function that appends data to a shared list, simulating shared memory usage in threading.
`run_thread_shared_memory`: Creates and starts threads to execute `thread_function` and waits for their completion.

```python
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
```

![Thread IPC Shared Memory](/Images/tsharedmem.png)

### Thread-Based IPC with Message Passing

Demonstrates message passing between threads using a Queue. Similar to process-based message passing but adapted for threading.

`thread_producer`: Produces messages and puts them into the queue.

`thread_consumer`: Consumes messages from the queue and terminates on receiving an "END" message.

`run_thread_message_passing`: Sets up the queue, starts producer and consumer threads, and handles their synchronization.

```python
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
```

![Thread IPC Message Passing](/Images/tmesspass.png)

## Parallel Text Processing

`process_segment` Function:

- Takes a start and end position, along with a file path, to process a segment of the file.

- It reads and converts the text in the given segment to uppercase and counts the frequency of each alphabet character, returning a dictionary of these counts.

```python
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
```

`merge_counts` Function:

- Takes a list of dictionaries (each representing character counts from file segments) and merges them into a single dictionary, summing up the counts for each character across all segments.

```python
def merge_counts(counts_list):
    """Merge character counts from all segments."""
    final_counts = {}
    for counts in counts_list:
        for char, count in counts.items():
            final_counts[char] = final_counts.get(char, 0) + count
    return final_counts
```

`main` Function:

- Initializes timing and resource usage monitoring.

- Determines the file size and divides the work into chunks based on the number of workers (threads) to create equally sized segments (except possibly the last one).

- Uses `ThreadPoolExecutor` to create a pool of threads, submitting each file segment to be processed in parallel by `process_segment`.

- Waits for all threads to complete and collects their results.

- Merges all partial counts into a final result using `merge_counts`.

- Prints the final character counts.

- Calculates and prints the execution time, CPU usage change, and memory usage increase from before to after the processing.

```python
def main(file_path):
    # Start timing and resource monitoring
    start_time = time.time_ns()
    process = psutil.Process()  # Get current Python process
    initial_cpu = process.cpu_percent(interval=None)
    initial_memory = process.memory_info().rss  # Resident Set Size: physical memory used

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
```

### Overview & Usage

The script is designed for efficiency in processing large files by utilizing multiple threads to handle different parts of the file simultaneously. This parallel processing approach can significantly speed up the computation, especially on multi-core systems. The resource usage monitoring provides insights into the performance characteristics of the script, such as how much CPU and memory it consumes during its execution.

Different sizes of files can be tested with the provided .txt's

`BeeMovie.txt` - 50 KB
`Frankenstein.txt` - 439 KB
`Dracula.txt` - 870 KB

![Bee Movie Test](/Images/beemovie.png)

![Frankenstein Test](/Images/frankenstein.png)

![Dracula Test](/Images/dracula.png)

## Discussion

### Challenges

### Structure

### Limitations

### Conclusion
