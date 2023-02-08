#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
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

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse as urlparse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    def get_host_port(self,url):
        parsed_url = urlparse.urlparse(url)
        print(f"\nparsed url is: {parsed_url}")
        print(f"\nThe Hostname is: {parsed_url.hostname}\n")
        print(f"The port is: {parsed_url.port}\n")
        print(f"The path given is: {parsed_url.path}\n")

        if parsed_url.port == None:
            if parsed_url.scheme == 'http':
                port = 80
            else:
                port = 443
            return parsed_url.hostname, port, parsed_url.path
        else:
            return parsed_url.hostname, parsed_url.port, parsed_url.path

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        data_split = data.split("\r\n")
        main_header = data_split[0].split(' ')
        print(main_header)
        code = main_header[1]
        return code

    def get_headers(self,data):
        # data_split = data.split("\r\n")
        data_split = data.split("\r\n\r\n")
        # main_header = data_split[0].split(' ')
        header = data_split[0]
        return header

    def get_body(self, data):
        data_split = data.split("\r\n\r\n")
        body = data_split[1]
        return body
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        host, port, path = self.get_host_port(url)
        print(f"the url is: {url}")
            
        self.connect(host, port)

        request = "GET "    
        if path: 
            request += path
        else:
            request += "/"
        if port == 80:
            request += " HTTP/1.1\nHost: " + host + ":" + str(port) + "\r\n" 
        else:
            request += " HTTP/1.1\nHost: " + host + "\r\n"
        request += "\n\n"

        print(f"the request is: \n{request}")

        self.sendall(request)
        data = self.recvall(self.socket)
        self.close()
        print(data)
        headers = self.get_headers(data)
        print(f"the headers is: {headers}")
        code = int(self.get_code(data))
        body = self.get_body(data)
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        host, port, path= self.get_host_port(url)
        self.connect(host, port)
        length = len(path)
        # request = "POST / HTTP/1.1\nHost:" + host + "\n\n"
        request = "POST " + path +  " HTTP/1.1\nHost:" + host + "\r\n" + "Content-Length:" + str(length) + "\n\n"
        print(f"\nThe reqeust to be sent to the server is: {request}\n")
        self.sendall(request)
        data = self.recvall(self.socket)
        # print(f"the POST data is: {data}")
        self.close()
        code = int(self.get_code(data))
        body = self.get_body(data)
        print(data)
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(sys.argv[2])
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
