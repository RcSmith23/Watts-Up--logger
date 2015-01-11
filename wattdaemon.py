#!/usr/bin/env python
#Socket server using select
import socket
import select
import wattsup
import dacapo

def main():
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
                    split = data.split(" ")
                    message = [ x.strip().lower() for x in split ]
                    print message[0]
                    # If length 1, checking if alive or logging
                    if len(message) == 1:
                        if message[0] == 'alive':
                            sock.send('Yes\n')
                        elif message[0] == 'log':
                            val = 'Yes\n' if logger.logging() else 'No\n'
                            sock.send(val)
                        else:
                            sock.send('Invalid Argument\n')
                    # Length 2: whether to start or stop logging
                    elif len(message) == 2:
                        if message[0] == 'log':
                            if message[1] == 'start' and not logger.logging():
                                try:
                                    logger.start()
                                except Exception as e:
                                    sock.send('Error Log\n')
                            elif message[1] == 'stop' and logger.logging():
                                try:
                                    logger.stop()
                                except Exception as e:
                                    sock.send('Error Log\n')
                    # Length > 2: run a benchmark
                    elif len(message) > 2:
                        if message[0] == 'bench' and message[1] == 'start':
                            if not logger.logging():
                                try:
                                    logger.start()
                                except Exception as e:
                                    sock.send('Error Run\n')
                            if not dacapo.running() and logger.logging():
                                try:
                                    dacapo.run(message[2:])
                                except Exception as e:
                                    sock.send('Error Run\n')
                except:
                    sock.close()
                    CONNECTION_LIST.remove(sock)
                    continue
    server_socket.shutdown()
    server_socket.close()

if __name__ == "__main__":
    main()

