import logging
import sys
import threading
from multiprocessing import Process, Queue
from queue import Empty

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class CustomProcess:
    def __init__(self, name):
        self.name = name
        self.message_queue = Queue()
        self.threads = []

    def run(self):
        while True:
            try:
                message = self.message_queue.get(timeout=3)  # Adjust timeout as needed
                logging.info(f"Process {self.name} received message: {message}")
            except Empty:
                break

class CustomThread:
    def __init__(self, name, target, args):
        self.name = name
        self.thread = threading.Thread(target=target, args=args, name=name)
        self.thread.start()

    def join(self):
        self.thread.join()

class ProcessManager:
    def __init__(self):
        self.processes = {}  # Stores Process instances, not CustomProcess instances

    def create_process(self, name):
        process = CustomProcess(name)
        p = Process(target=process.run)
        p.start()
        self.processes[p.pid] = p  # Store the Process instance, not the CustomProcess instance
        logging.info(f"Process {name} with PID {p.pid} created.")

    def terminate_process(self, pid):
        if pid in self.processes:
            p = self.processes[pid]
            p.terminate()  # Now correctly terminates the Process instance
            p.join()
            del self.processes[pid]
            logging.info(f"Process with PID {pid} terminated.")
        else:
            logging.error(f"Process with PID {pid} not found.")

    def list_processes(self):
        logging.info("List of running processes:")
        for pid in self.processes:
            # Logging the process PID and the name attribute from the CustomProcess instance, if needed
            logging.info(f"PID: {pid}, Name: {self.processes[pid]}")

    def send_message(self, source_pid, target_pid, message):
        if target_pid in self.processes:
            target_process = self.processes[target_pid]
            target_process.message_queue.put(f"From PID {source_pid}: {message}")
            logging.info(f"Message sent from PID {source_pid} to PID {target_pid}: {message}")
        else:
            logging.error("Invalid target PID.")

if __name__ == "__main__":
    process_manager = ProcessManager()

    while True:
        command = input("Enter a command (create/list/terminate/send_message/exit): ")
        if command == "create":
            name = input("Enter the process name: ")
            process_manager.create_process(name)
        elif command == "list":
            process_manager.list_processes()
        elif command == "terminate":
            pid = int(input("Enter the PID of the process to terminate: "))
            process_manager.terminate_process(pid)
        elif command == "send_message":
            source_pid = int(input("Enter the source PID: "))
            target_pid = int(input("Enter the target PID: "))
            message = input("Enter the message: ")
            process_manager.send_message(source_pid, target_pid, message)
        elif command == "exit":
            logging.info("Exiting the Process Manager.")
            sys.exit()
        else:
            logging.error("Invalid command. Please try again.")
