import socket
import threading
import os
import sys

# Directory to serve files from, to be set from command-line argument
file_directory = ""

def handle_client(conn,addr):
    with conn:
        print(f"Connected by {addr}")
        request = conn.recv(1024)
        request_str = request.decode()
        request_lines = request_str.split("\r\n")
        request_line = request_lines[0]
        headers = request_lines[1:]
        
        url = request_line.split(" ")[1]
        user_agent = ""
        
        for header in headers:
            if header.startswith("User-Agent:"):
                user_agent = header.split(":", 1)[1].strip()
                break

        if url == "/":
            conn.send(b"HTTP/1.1 200 OK\r\n\r\n")
        
        elif url.startswith("/echo/"):
            echo_str = url[len("/echo/"):]
            response_body = echo_str.encode()
            content_length = len(response_body)
            response = (
                b"HTTP/1.1 200 OK\r\n"
                b"Content-Type: text/plain\r\n"
                b"Content-Length: " + str(content_length).encode() + b"\r\n\r\n" +
                response_body
            )
            conn.send(response)
        
        elif url == "/user-agent":
            response_body = user_agent.encode()
            content_length = len(response_body)
            response = (
                b"HTTP/1.1 200 OK\r\n"
                b"Content-Type: text/plain\r\n"
                b"Content-Length: " + str(content_length).encode() + b"\r\n\r\n" +
                response_body
            )
            conn.send(response)
        
        elif url.startswith("/files/"):
            filename = url[len("/files/"):]
            file_path = os.path.join(file_directory, filename)
            
            print(f"Requested file path: {file_path}")
            
            if os.path.exists(file_path) and os.path.isfile(file_path):
                with open(file_path, "rb") as f:
                    file_content = f.read()
                content_length = len(file_content)
                response = (
                    b"HTTP/1.1 200 OK\r\n"
                    b"Content-Type: application/octet-stream\r\n"
                    b"Content-Length: " + str(content_length).encode() + b"\r\n\r\n" +
                    file_content
                )
                conn.send(response)
            else:
                print(f"File not found: {file_path}")
                conn.send(b"HTTP/1.1 404 Not Found\r\n\r\n")
        else:
            conn.send(b"HTTP/1.1 404 Not Found\r\n\r\n")
        
        conn.close()

def main():
    global file_directory
    
    # Ensure directory is passed as a command-line argument
    if len(sys.argv) != 3 or sys.argv[1] != "--directory":
        print("Usage: ./your_server.sh --directory <directory_path>")
        return

    file_directory = sys.argv[2]
    
    # Print statements for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")
    
    server_socket = socket.create_server(("localhost", 4221))
    print("Server is running on port 4221...")

    try:
        while True:
            conn, addr = server_socket.accept()  # wait for client
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.start()
    except KeyboardInterrupt:
        print("Server is shutting down...")
    finally:
        server_socket.close()

if __name__ == "__main__":
    main()