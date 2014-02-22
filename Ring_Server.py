import subprocess,urllib,httplib,json,time,thread,PlayerCore
from SocketServer import TCPServer,StreamRequestHandler,ThreadingMixIn

ring_time = "12-42"

class Server(TCPServer,ThreadingMixIn):pass

class Handler(StreamRequestHandler):

    def handle(self):
        addr = self.request.getpeername()
        print "Client is Connect IP:",addr
        data = True
        while data:
            data = self.request.recv(2048)
            print "receive data:" + data ,addr
            if data == "Play":
                PlayerCore.play()
            elif data == "Next":
                PlayerCore.playNext()
                    

def ringer():
    while True:
        global ring_time
        now_time = time.strftime('%H-%M',time.localtime(time.time()))
        if ring_time == now_time:
            print "It's time"
            PlayerCore.ring()
        time.sleep(10)

thread.start_new_thread(ringer,())


server = Server(('',7777),Handler)
print 'waiting for connection...'
server.serve_forever()