import socket
import threading
import os

HOST = '0.0.0.0'
PORT = 5000

def handle_receive(conn):
    while True:
        try:
            header = conn.recv(1024)
            if not header:
                print("Client disconnected.")
                break
            data_str = header.decode('utf-8', errors='replace')
            lines = data_str.split('\n')
            first_line = lines[0].strip()

            if first_line.startswith("FILE "):
                parts = first_line.split(' ')
                if len(parts) == 3:
                    _, filename, filesize_str = parts
                    filesize = int(filesize_str)
                    file_data = b''
                    remaining = filesize
                    while remaining > 0:
                        chunk = conn.recv(min(4096, remaining))
                        if not chunk:
                            print("Connection lost")
                            break
                        file_data += chunk
                        remaining -= len(chunk)

                    with open(filename, 'wb') as f:
                        f.write(file_data)

                    print(f"Received file '{filename}' ({filesize} bytes).")
                else:
                    print("invalid header")
            else:
                print(f"Client: {first_line}")

        except Exception as e:
            print("Error receiving data:", e)
            break

    conn.close()

def handle_send(conn):
    while True:
        msg = input("")
        if msg.startswith("FILE "):
            parts = msg.split(' ', 1)
            if len(parts) == 2:
                filename = parts[1].strip()
                if os.path.exists(filename):
                    filesize = os.path.getsize(filename)
                    header = f"FILE {filename} {filesize}\n".encode('utf-8')
                    conn.sendall(header)
                    with open(filename, 'rb') as f:
                        chunk = f.read(4096)
                        while chunk:
                            conn.sendall(chunk)
                            chunk = f.read(4096)
                    print(f"Sent file '{filename}'.")
                else:
                    print("File does not exist.")
            else:
                print("invalid command")
        else:
            to_send = (msg + "\n").encode('utf-8')
            conn.sendall(to_send)

def start_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen(1)
    print(f"Server listening on {HOST}:{PORT}...")
    conn, addr = s.accept()
    print("Client connected from", addr)
    recv_thread = threading.Thread(target=handle_receive, args=(conn,))
    send_thread = threading.Thread(target=handle_send, args=(conn,))
    recv_thread.start()
    send_thread.start()

    recv_thread.join()
    send_thread.join()

if __name__ == "__main__":
    start_server()