#  coding: utf-8 
import socketserver
import re
import os

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

    def detect_method(self):
        methods = re.findall(r'^(.+?) ', self.data.decode('utf-8'))
        method = methods[0]

        # only accept GET
        if method == 'GET':
            return method
        else:
            return 405

    def get_path(self):
        # find all matched file names by regular expression
        paths = re.findall(r'GET (.+?) HTTP', self.data.decode('utf-8'))
        path = paths[0]       # get the first match

        # add relative directory of ./www folder
        path = 'www' + path
        
        # if the file name end with '/' then return index.html 
        if path[-1] == '/':
            path += 'index.html'

        return path
    
    def check_path(self, path):
        dir_status = os.path.isdir(path)
        file_status = os.path.isfile(path)

        # check if the given path is a sub directory of 'www' foler for security reason
        input_path = os.path.realpath(path)
        web_path = os.path.realpath('www')
        sub_path = input_path.startswith(web_path)

        if dir_status and not file_status and sub_path:
            return 301
        elif not dir_status and file_status and sub_path:
            return 200
        else:
            return 404

    def get_mime_type(self, path):
        # path = 'www/test.org/index.html'
        # find all matched file type by regular expression

        if path.endswith('.html'):
            mime_type = 'text/html'
        elif path.endswith('.css'):
            mime_type = 'text/css'
        else:
            mime_type = ''

        return mime_type
    
    def handle(self):
        self.data = self.request.recv(1024).strip()
        print ("Got a request of: %s\n" % self.data)
        # self.request.sendall(bytearray("OK",'utf-8'))

        # parse request
        try:
            method = self.detect_method()
            if method == 405:
                raise Exception(405, '405 Method Not Allowed')

            path = self.get_path()
            # check if the file exists
            path_status = self.check_path(path)
            if path_status == 301:
                raise Exception(301, path[4:] + '/')       # return a relative URL
            elif path_status == 404:
                raise Exception(404, '404 Not Found')

            mime_type = self.get_mime_type(path)

            content_length = os.path.getsize(path)

            with open(path, 'r') as rfile:
                rfile_data = rfile.read()

            response = 'HTTP/1.1 200 OK\r\nContent-Length: ' + str(content_length) + '\r\nContent-Type: ' + mime_type + '\r\n\r\n' + rfile_data
        except Exception as e:
            code, info = e.args
            
            if code == 405:
                body = '<!doctype html><title>405 Method Not Allowed</title><h1>405 Method Not Allowed</h1>Only GET allowed'
                response = 'HTTP/1.1 405 Method Not Allowed\r\nContent-Length: ' + str(len(body.encode('utf-8'))) + '\r\nContent-Type: text/html\r\n\r\n' + body
            elif code == 301:
                body = '<!doctype html><title>301 Moved Permanently</title><h1>301 Moved Permanently</h1>The document has moved<A HREF=\"' + info + '\">here</A>'
                response = 'HTTP/1.1 301 Moved Permanently\r\nLocation: ' + info + '\r\nContent-Length: ' + str(len(body.encode('utf-8'))) + '\r\nContent-Type: text/html\r\n\r\n' + body
            elif code == 404:
                body = '<!doctype html><title>404 Not Found</title><h1>404 Not Found</h1>'
                response = 'HTTP/1.1 404 Not Found\r\nContent-Length: ' + str(len(body.encode('utf-8'))) + '\r\nContent-Type: text/html\r\n\r\n' + body
        finally:
            self.request.sendall(bytearray(response,'utf-8'))

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()