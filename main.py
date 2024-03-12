import socket
import threading
import time
import random

class LogicalClock:
    def __init__(self, process_id, port):
        self.process_id = process_id
        self.port = port
        self.vector = [0] * 4 

    def increment(self):
        self.vector[self.process_id - 1] += 1

    def update(self, received_vector):
        for i in range(len(self.vector)):
            self.vector[i] = max(self.vector[i], received_vector[i])

    def __str__(self):
        return f"P{self.process_id}: {self.vector}"

def send_message(process_id, port, message, vector):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        receiver_port = random.randint(5001, 5004)
        s.connect(('localhost', receiver_port))
        s.sendall(f"{port}|{message}|{vector}".encode())
        print(f"P{process_id} sending message to P{receiver_port - 5000}: {vector}")

def receive_messages(process_id, port, vector):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('localhost', port))
        s.listen()
        while True:
            conn, _ = s.accept()
            data = conn.recv(1024).decode()
            sender_port_str, received_message, received_vector_str = data.split('|')
            received_vector_splitted = received_vector_str[1:-1].split(',')
            received_vector = [int(x) for x in received_vector_splitted]
            vector.update(received_vector)
            vector.increment()
            sender_port = int(sender_port_str)
            print(f"P{process_id} received message {received_message} {received_vector_str} from P{sender_port - 5000}")
            print(f"P{process_id} updated vector: {vector}")

def main(process_id, port):
    clock = LogicalClock(process_id, port)
    threading.Thread(target=receive_messages, args=(process_id, port, clock)).start()
    while True:
        time.sleep(random.randint(1, 4))
        clock.increment()
        send_message(process_id, port, "I am a message!", clock.vector)

if __name__ == "__main__":
    processes = [(1, 5001), (2, 5002), (3, 5003), (4, 5004)]
    for process_id, port in processes:
        threading.Thread(target=main, args=(process_id, port)).start()
