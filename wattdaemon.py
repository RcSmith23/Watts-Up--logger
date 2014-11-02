'''
    Socket server testing with threads
'''

import socket
import sys
from thread import *

HOST = ''
PORT = 8888

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print 'Socket Created'

#Binding the socket to the local host and port
try:
    s.bind((HOST, PORT))
except socket.error as msg:
    print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
    sys.exit()

print 'Socket bind complete'

#Start listening
s.listen(10)
print 'Socket now listening'

#for handling each connectiong
def client_thread(conn):
    #send message to client
    #send only takes a string
    conn.send('Welcome to the server. Tpye something and hit enter\n')
    while True:
        data = conn.recv(1024)
        reply = 'Ok...' + data
        if not data:
            break

        conn.sendall(reply)

    conn.close()

#now to talk with client
while 1:
    #wait for a connection
    conn, addr = s.accept()
    print 'Connected with ' + addr[0] + ':' + str(addr[1])

    start_new_thread(client_thread, (conn,))

s.close()
