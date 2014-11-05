#!/usr/bin/env python
#Socket server using select
import socket
import select

if __name__ == "__main__":

    CONNECTION_LIST = []
    RECV_BUFFER = 1024
    PORT = 44000

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(("0.0.0.0", PORT))
    server_socket.listen(5)

    #add the socket to the connections list
    CONNECTION_LIST.append(server_socket)

    #possible print, see where to print for daemon service

    while True:
        read_sockets, write_sockets, error_sockets = \
                        select.select(CONNECTION_LIST,[],[])

        for sock in read_sockets:
            #new client
            if sock == server_socket:
                sockfd, addr = server_socket.accept()
                CONNECTION_LIST.append(sockfd)
            #incoming message
            else:
                try:
                    data = sock.recv(RECV_BUFFER)
                    #here need to parse data and execute
                    if data:
                        sock.send('Ok...' + data)
                except:
                    sock.close()
                    CONNECTION_LIST.remove(sock)
                    continue
    server_socket.shutdown()
    server_socket.close()
