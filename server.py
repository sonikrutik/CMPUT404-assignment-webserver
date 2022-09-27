#  coding: utf-8 
import socketserver, os, re

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
        self.data = self.request.recv(1024).strip()
        print ("Got a request of: %s\n" % self.data)
        self.request.sendall(bytearray("OK",'utf-8'))

        try: 
            requestName = self.getServerToken()
            if requestName == 'GET':
                
                self.do405(requestName)
            else:
                raise Exception(requestName)

        except Exception as e:
            statusCode = e.args
            self.do405(statusCode)
            

    def doGET(self, requestName):
        body = '<html><title>{fname}</title><h1>{fname}</h1>Only GET allowed'.format(fname = requestName)
        response = 'HTTP/1.1 200 GOOD SHIT\r\nContent-Length: ' + str(len(body.encode('utf-8'))) + '\r\nContent-Type: text/html\r\n\r\n' + body
        self.request.sendall(bytearray(response, 'utf-8'))
        
    def do405(self, statusCode):
        body = '<html><title>{fname}</title><h1>{fname}</h1>Only GET allowed'.format(fname = statusCode)
        response = 'HTTP/1.1 {fname}\r\nContent-Length: '.format(fname = statusCode) + str(len(body.encode('utf-8'))) + '\r\nContent-Type: text/html\r\n\r\n' + body
        self.request.sendall(bytearray(response, 'utf-8'))

    def getServerToken(self):

        serverToken = re.findall(r'^(.+?) ', self.data.decode('utf-8'))[0]
        if serverToken == 'GET': 
            print("COCK AND BALLS MFER")
            return serverToken
        
        return 405


if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)
    print("Starting server now!")
    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
