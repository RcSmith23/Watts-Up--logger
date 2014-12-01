#!/usr/bin/env python
#Socket server using select
import socket
import select
import wattsup
import dacapo

if __name__ == "__main__":

    logger = wattsup.WattsUp()
    dacapo = dacapo.DacapoSuite()

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

    while 1:
        read_sockets, write_sockets, error_sockets = \
                        select.select(CONNECTION_LIST,[],[])

        for sock in read_sockets:
            #new client
            if sock == server_socket:
                sockfd, addr = server_socket.accept()
                CONNECTION_LIST.append(sockfd)
                print "New client"
            #incoming message
            else:
                try:
                    # Here need to parse data and execute
                    data = sock.recv(RECV_BUFFER)
                    message = data.split(" ")
                    print message[0]
                    # If length 1, checking if alive or logging
                    if len(message) == 1:
                        if message[0] == 'Alive':
                            sock.send('Yes')
                        elif message[0] == 'Log':
                            val = 'Yes' if logger.logging() else 'No'
                            sock.send(val)
                        else:
                            sock.send('Invalid')
                    # Length 2: whether to start or stop logging
                    elif len(message) == 2:
                        if message[0] == 'Log':
                            if message[1] == 'Start' and not logger.logging():
                                try:
                                    logger.start()
                                except Exception as e:
                                    sock.send('Error Log')
                            elif message[1] == 'Stop' and logger.logging():
                                try:
                                    logger.stop()
                                except Exception as e:
                                    sock.send('Error Log')
                    # Length > 2: run a benchmark
                    elif len(message) > 2:
                        if message[0] == 'Bench' and message[1] == 'Start':
                            if not logger.logging():
                                try:
                                    logger.start()
                                except Exception as e:
                                    sock.send('Error Run')
                            if not dacapo.running() and logger.logging():
                                try:
                                    dacapo.run(message[2:])
                                except Exception as e:
                                    sock.send('Error Run')
                except:
                    sock.close()
                    CONNECTION_LIST.remove(sock)
                    continue
    server_socket.shutdown()
    server_socket.close()
