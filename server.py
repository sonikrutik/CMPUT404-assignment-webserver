#  coding: utf-8 
from genericpath import isfile
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
        #self.request.sendall(bytearray("OK",'utf-8'))

        requestName = self.getServerToken()
        # if requestName == 'GET':
        if requestName != 'GET':
            self.do405(requestName)

        if re.findall(r'GET (.+?) HTTP', self.data.decode('utf-8')) == []:
            self.do404(404, "Not Found")
        
        else:
            path = 'www' + re.findall(r'GET (.+?) HTTP', self.data.decode('utf-8'))[0]
            print(re.findall(r'GET (.+?) HTTP', self.data.decode('utf-8')))
            #path = "./www/" + self.request.recv(1024).decode("utf-8").strip().split()[1][1:]

            print(path)

            if path[-1] == '/':
                path += 'index.html'

            #print(path)
            isDir = os.path.isdir(path) #check if the path is a directory
            isFile = os.path.isfile(path) #check if the path is a file!
            #print(isDir, isFile, os.path.realpath(path))
            
            onlyWebPath = os.path.realpath('www') # gets path until www
            subPath = os.path.realpath(path).startswith(onlyWebPath) # checks if path starts and ends until www (a path is found or not 404)
            #print(subPath, os.path.realpath(path), webPath)
            #print(requestName, os.getcwd(), "\n", path)
            print(path[4:], "ABDJHASDKILASDA")
            if not isDir and isFile and subPath:
                self.doGET(path)

            elif isDir and not isFile and subPath:
                self.do301(301, "Moved Permenantly", path[4:] + '/') # if direcoty exists but not file raise 301 to say file has moved
            
            else:
                self.do404(404, "Not Found")
                
        
        

            
    def mimeType(self, path):
        if path.endswith('.html'):
            return 'text/html'

        elif path.endswith('.css'):
            return 'text/css'

        else: 
            return ''

    
    def doGET(self, path):
        print("200")

        mime = self.mimeType(path)
                    
        with open(path, 'r') as rfile:
            fileData = rfile.read()

        response = 'HTTP/1.1 200 OK\r\nContent-Length: ' + str(os.path.getsize(path)) + '\r\nContent-Type: ' + mime + '\r\n\r\n' + fileData
        self.request.sendall(bytearray(response, 'utf-8'))

    def do405(self, statusCode):
        print("405")
        body = '<html><title>{fname} Method Not Allowed</title><h1>{fname}</h1>'.format(fname = statusCode)
        response = 'HTTP/1.1 {fname}\r\nContent-Length: '.format(fname = statusCode) + str(len(body.encode('utf-8'))) + '\r\nContent-Type: text/html\r\n\r\n' + body
        self.request.sendall(bytearray(response, 'utf-8'))

    def do301(self, statusCode, Message, location):
        print("301")
        body = '<html><title>{code} {message}</title><h1>{code} {message}</h1>'.format(code = statusCode, message = Message)
        response = 'HTTP/1.1 {code} {message}\r\nLocation: '.format(code = statusCode, message = Message) + location + '\r\nContent-Length: ' + str(len(body.encode('utf-8'))) + '\r\nContent-Type: text/html\r\n\r\n' + body
        self.request.sendall(bytearray(response, 'utf-8'))
    def do404(self, statusCode, Message):
        print("404")
        body = '<html><title>{code} {message}</title><h1>{code} {message}</h1>'.format(code = statusCode, message = Message)
        response = 'HTTP/1.1 {code} {message}\r\nContent-Length: '.format(code = statusCode, message = Message) + str(len(body.encode('utf-8'))) + '\r\nContent-Type: text/html\r\n\r\n' + body
        self.request.sendall(bytearray(response, 'utf-8'))

    def getServerToken(self):

        serverToken = re.findall(r'^(.+?) ', self.data.decode('utf-8'))[0]
        if serverToken == 'GET': 
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
