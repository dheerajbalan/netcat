#!/usr/bin/env python3
import argparse
import socket
import threading
import shlex
import sys
import textwrap
import subprocess


def execute(cmd):
    """Execute a shell command and return the output."""
    if not cmd:
        return b''
    output = subprocess.check_output(shlex.split(cmd), stderr=subprocess.STDOUT)
    return output

class NetCat:
    def __init__(self, args, buffer=None):
        self.args = args
        self.buffer = buffer
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.client_threads = []
        self.should_shutdown = threading.Event()

    def run(self):
        if self.args.listen:
            self.listen()
        else:
            self.send()

    def send(self):
        self.socket.connect((self.args.target, self.args.port))
        if self.buffer:
            self.socket.send(self.buffer.encode())
        try:
            while True:
                response = b""
                while True:
                    data = self.socket.recv(4096)
                    if not data:
                        break
                    response += data
                if response:
                    print(response.decode())
                    buffer = input("> ")
                    buffer += "\n"
                    self.socket.send(buffer.encode())
        except KeyboardInterrupt:
            print("Session terminated.")
            self.socket.close()
            sys.exit()

    def listen(self):
        self.socket.bind((self.args.target, self.args.port))
        self.socket.listen(5)
        print(f"[*] Listening on {self.args.target}:{self.args.port}")
        try:
            while not self.should_shutdown.is_set():
                try:
                    self.socket.settimeout(1.0)
                    client_socket, _ = self.socket.accept()
                    client_thread = threading.Thread(target=self.handle, args=(client_socket,))
                    client_thread.start()
                    self.client_threads.append(client_thread)
                except socket.timeout:
                    continue
        except KeyboardInterrupt:
            self.should_shutdown.set()
            self.shutdown()
            print("\nServer shutdown.")
            sys.exit()

    def handle(self, client_socket):
        if self.args.execute:
            output = execute(self.args.execute)
            client_socket.send(output)

        elif self.args.upload:
            print(f"[*] Uploading file to {self.args.upload}")
            file_buffer = b""
            while True:
                data = client_socket.recv(4096)
                if not data:
                    break
                print(f"Received {len(data)} bytes")
                file_buffer += data
            try:
                with open(self.args.upload, "wb") as f:
                    f.write(file_buffer)
                client_socket.send(f"File saved: {self.args.upload}\n".encode())
                print(f"[+] File saved successfully to {self.args.upload}")
            except Exception as e:
                client_socket.send(f"Failed to save file: {e}\n".encode())
                print(f"[-] Failed to save file: {e}")

        elif self.args.command:
            while True:
                cmd_buffer = b""
                try:
                    client_socket.send(b"BHP: #> ")
                    while b'\n' not in cmd_buffer:
                        cmd_buffer += client_socket.recv(64)
                    cmd = cmd_buffer.decode().strip()
                    if cmd:
                        response = execute(cmd)
                        if response:
                            client_socket.send(response)
                    cmd_buffer = b""
                except Exception as e:
                    print(f"Server killed: {e}")
                    client_socket.close()
                    break
        client_socket.close()

    def shutdown(self):
        self.should_shutdown.set()
        self.socket.close()
        for t in self.client_threads:
            t.join()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='BHP Net Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent('''Example:
            netcat.py -t 192.168.1.108 -p 5555 -l -c # Command shell
            netcat.py -t 192.168.1.108 -p 5555 -l -u=mytest.txt # Upload a file
            netcat.py -t 192.168.1.108 -p 5555 -l -e="cat /etc/passwd" # Execute a command
            echo 'ABC' | ./netcat.py -t 192.168.1.108 -p 5555 # Echo text to server port 5555
            netcat.py -t 192.168.1.108 -p 5555 # Connect to a server
        ''')
    )
    parser.add_argument('-c', '--command', action='store_true', help='Initialize a command shell')
    parser.add_argument('-e', '--execute', help='Execute a specific command')
    parser.add_argument('-l', '--listen', action='store_true', help='Listen on [host]:[port] for incoming connections')
    parser.add_argument('-p', '--port', type=int, default=5555, help='Specify the port to listen on or connect to')
    parser.add_argument('-t', '--target', default='0.0.0.0', help='Specify the target IP address or hostname')
    parser.add_argument('-u', '--upload', help='Specify the path to upload a file to the target')
    args = parser.parse_args()

    if args.listen:
        buffer = ''
    else:
        buffer = sys.stdin.read()

    nc = NetCat(args, buffer)
    nc.run()
