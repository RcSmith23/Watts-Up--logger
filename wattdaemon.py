#!/usr/bin/env python
#Socket server using select
import socket
import select

if __name__ == "__main__":

    logger = WattsUp()
    dacapo = DacapoSuite()

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
                    data.split(" ")
                    #here need to parse data and execute
                    if data.length == 1:
                        if data[0] == 'Alive':
                            sock.send('Yes')
                        elif data[0] == 'Log':
                            val = 'Yes' if logger.logging else 'No'
                            sock.send(val)
                    elif data.length == 2:
                        if data[0] == 'Log':
                            if data[1] == 'Start' and not logger.logging:
                                logger.start()
                            elif data[1] == 'Stop' and logger.logging:
                                logger.stop()
                except:
                    sock.close()
                    CONNECTION_LIST.remove(sock)
                    continue
    server_socket.shutdown()
    server_socket.close()
