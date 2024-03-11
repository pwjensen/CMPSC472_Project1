# Import required modules
import logging # Used for logging messages.
import sys
import threading # For creating and managing threads.
from multiprocessing import Process, Event as ProcessEvent # Process for creating separate processes, Event for synchronization.
import time # For simulating work with sleep.
import queue # For managing commands in a queue.

# Set up basic configuration for logging system. Log messages include timestamp, severity level, and message.
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Defines a custom process with pause and resume capabilities.
class CustomProcess:
    # Initialize with a name and a pause_event for controlling the execution flow.
    def __init__(self, name):
        self.name = name
        self.pause_event = ProcessEvent()
        self.pause_event.set() # Initially set to True to allow running.

    def run(self):
        # Main loop of the process. Logs start message and enters an infinite loop that can be paused or resumed.
        logging.info(f"Process {self.name} started.")
        while True:
            self.pause_event.wait() # Blocks until pause_event is True.
            time.sleep(1)  # Simulates work by sleeping.

class CustomThread:
    def __init__(self, name):
        self.name = name
        self.pause_event = threading.Event()
        self.pause_event.set() # Initially set to True to allow running.

    def run(self):
        # Main loop of the thread. Logs start message and enters an infinite loop that can be paused or resumed.
        logging.info(f"Thread {self.name} started.")
        while True:
            self.pause_event.wait() # Blocks until pause_event is True.
            time.sleep(1)  # Simulates work by sleeping.

# Manages multiple processes, allowing creation, pausing, resuming, and termination.
class ProcessManager:
    # Initializes with empty dictionaries for tracking processes and their names to PIDs.
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

# Manages multiple threads, allowing creation, pausing, and resuming.
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

# Provides a command-line interface for interacting with the ProcessManager and ThreadManager.
class CLIManager(threading.Thread):
    def __init__(self, process_manager, thread_manager):
        # Initializes with references to a process manager and a thread manager.
        super().__init__()
        self.process_manager = process_manager
        self.thread_manager = thread_manager
        self.commands = queue.Queue()

    def run(self):
        # Main loop for processing commands. Exits on receiving the "exit" command.
        # Commands are fetched from the queue and executed using the execute_command method.
        while True:
            command = self.commands.get()
            if command[0] == "exit":
                logging.info("Exiting the Manager.")
                break
            self.execute_command(command)
            time.sleep(0.5)  # Give time for logging messages to be processed

    def execute_command(self, command):
        # Parses and executes commands to manage processes and threads. Supports operations like create, list, pause, resume, and terminate.
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
        # Adds a command to the queue for processing.
        self.commands.put(command)

if __name__ == "__main__":
    process_manager = ProcessManager()
    thread_manager = ThreadManager()
    cli_manager = CLIManager(process_manager, thread_manager)
    cli_manager.start()

    while True:
        command = input("Enter a command (create/list/pause/resume/terminate/exit) and type (process/thread): ").split()
        cli_manager.submit_command(command)
        if command[0] == "exit":
            break
        time.sleep(0.5)  # Give time for logging messages to be processed before the next prompt
