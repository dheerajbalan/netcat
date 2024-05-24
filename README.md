
NetCat is a Python implementation of the classic Netcat tool, providing a versatile and powerful way to interact with network services. It allows you to create both client and server connections, execute commands remotely, upload and download files, and more.

Features

Command Shell: Initiate a command shell on the target machine.
Execute Commands: Execute a specific command on the target machine.
Upload Files: Upload files to the target machine.
Multiple Connections: Handle multiple client connections concurrently using threading.
Flexible Usage: Supports both listening and connecting modes.

Usage

sql

usage: netcat.py [-h] [-c] [-e EXECUTE] [-l] [-p PORT] [-t TARGET] [-u UPLOAD]

BHP Net Tool

optional arguments:
  -h, --help            show this help message and exit
  -c, --command         Initialize a command shell
  -e EXECUTE, --execute EXECUTE
                        Execute a specific command
  -l, --listen          Listen on [host]:[port] for incoming connections
  -p PORT, --port PORT  Specify the port to listen on or connect to
  -t TARGET, --target TARGET
                        Specify the target IP address or hostname
  -u UPLOAD, --upload UPLOAD
                        Specify the path to upload a file to the target

Examples

Initialize a command shell:


	python3 netcat.py -t 192.168.1.108 -p 5555 -l -c

Upload a file to the target:



	python3 netcat.py -t 192.168.1.108 -p 5555 -l -u=mytest.txt

Execute a command on the target:



    python3 netcat.py -t 192.168.1.108 -p 5555 -l -e="cat /etc/passwd"

License

This project is licensed under the MIT License - see the LICENSE file for details.
