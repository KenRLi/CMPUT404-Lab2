import socket
import time
import sys
from multiprocessing import Process

HOST = ""
PORT = 8001
BUFFER_SIZE = 1024

def getRemoteIP(host):
    print(f"Getting IP for {host}")
    try:
        remoteIP = socket.gethostbyname(host)
    except socket.gaierror:
        print("Hostname could not be resolved. Exiting.")
        sys.exit()
    print(f"IP address of {host} is {remoteIP}")
    return remoteIP

def handleRequest(conn, addr, proxy_end):
    receivedClientData = conn.recv(BUFFER_SIZE)
    print(f"Sending received data {receivedClientData} to Google")
    proxy_end.sendall(receivedClientData)
    proxy_end.shutdown(socket.SHUT_WR)

    googleData = proxy_end.recv(BUFFER_SIZE)
    print(f"Sending received data {googleData} to client")
    conn.send(googleData)

def main():
    host = "www.google.com"
    port = 80

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as proxy_start:
        print("Starting proxy server")
        proxy_start.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        proxy_start.bind((HOST,PORT))
        proxy_start.listen(1)

        while(True):
            conn, addr = proxy_start.accept()
            print("Connected by", addr)
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as proxy_end:
                print("Connecting to Google")
                remoteIP = getRemoteIP(host)

                proxy_end.connect((remoteIP, port))

                p = Process(target=handleRequest, args=(conn, addr, proxy_end))
                p.daemon = True
                p.start()
                print("Started process", p)

            conn.close()

if __name__ == "__main__":
    main()