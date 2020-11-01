from socket import *
import threading

HOST = '0.0.0.0'
PORT = 3306
BUFSIZ = 4096000
ADDR = (HOST,PORT)

FORWARDHOST = '192.168.1.2' # pointing to a forwarding virtual machine
FORWARDPORT = 3306
FORWARDADDR = (FORWARDHOST,FORWARDPORT)

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

ct = ClientThread(tcpCliSock, tcpServerSock)
st = ServerThread(tcpCliSock, tcpServerSock)
ct.start()
st.start()
