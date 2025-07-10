#!/usr/bin/env python3
"""
Local development server for Swedenborg Reader
Serves static files and handles API requests on /api/index
"""
import http.server
import socketserver
import json
import urllib.parse
from pathlib import Path
import os
import sys

# Import the handler from the API
sys.path.append(os.path.join(os.path.dirname(__file__), 'api'))
from index import handler

class DevHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        # Handle API requests
        if self.path.startswith('/api/index'):
            try:
                # Create a mock request object for the handler
                class MockRequest:
                    def __init__(self, method, path, headers, body):
                        self.method = method
                        self.path = path
                        self.headers = headers
                        self.body = body
                        self.rfile = MockFile(body)
                
                class MockFile:
                    def __init__(self, content):
                        self.content = content
                        self.pos = 0
                    
                    def read(self, size=-1):
                        if size == -1:
                            result = self.content[self.pos:]
                            self.pos = len(self.content)
                        else:
                            result = self.content[self.pos:self.pos + size]
                            self.pos += len(result)
                        return result

                # Read the request body
                content_length = int(self.headers.get('content-length', 0))
                body = self.rfile.read(content_length)
                
                # Create the handler instance with proper initialization
                api_handler = handler(None, None, None)
                api_handler.headers = self.headers
                api_handler.rfile = MockFile(body)
                
                # Mock the response methods
                response_status = 200
                response_headers = {}
                response_body = b""
                
                def mock_send_response(status):
                    nonlocal response_status
                    response_status = status
                
                def mock_send_header(name, value):
                    response_headers[name] = value
                
                def mock_end_headers():
                    pass
                
                def mock_write(data):
                    nonlocal response_body
                    response_body += data
                
                api_handler.send_response = mock_send_response
                api_handler.send_header = mock_send_header
                api_handler.end_headers = mock_end_headers
                api_handler.wfile = type('MockWfile', (), {'write': mock_write})()
                
                # Call the POST handler
                api_handler.do_POST()
                
                # Send the response
                self.send_response(response_status)
                for name, value in response_headers.items():
                    self.send_header(name, value)
                self.end_headers()
                self.wfile.write(response_body)
                
            except Exception as e:
                print(f"API Error: {e}")
                self.send_response(500)
                self.send_header("Content-type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                error_response = {"error": f"Server error: {str(e)}"}
                self.wfile.write(json.dumps(error_response).encode())
        else:
            # For non-API POST requests, return 405 Method Not Allowed
            self.send_response(405)
            self.end_headers()
    
    def do_GET(self):
        # Handle API GET requests
        if self.path.startswith('/api/index'):
            try:
                # Create the handler instance with proper initialization
                api_handler = handler(None, None, None)
                
                # Mock the response methods
                response_status = 200
                response_headers = {}
                response_body = b""
                
                def mock_send_response(status):
                    nonlocal response_status
                    response_status = status
                
                def mock_send_header(name, value):
                    response_headers[name] = value
                
                def mock_end_headers():
                    pass
                
                def mock_write(data):
                    nonlocal response_body
                    response_body += data
                
                api_handler.send_response = mock_send_response
                api_handler.send_header = mock_send_header
                api_handler.end_headers = mock_end_headers
                api_handler.wfile = type('MockWfile', (), {'write': mock_write})()
                
                # Call the GET handler
                api_handler.do_GET()
                
                # Send the response
                self.send_response(response_status)
                for name, value in response_headers.items():
                    self.send_header(name, value)
                self.end_headers()
                self.wfile.write(response_body)
                
            except Exception as e:
                print(f"API Error: {e}")
                self.send_response(500)
                self.send_header("Content-type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                error_response = {"error": f"Server error: {str(e)}"}
                self.wfile.write(json.dumps(error_response).encode())
        else:
            # For static files, use the parent class handler
            super().do_GET()
    
    def do_OPTIONS(self):
        # Handle CORS preflight requests
        if self.path.startswith('/api/'):
            # Create the handler instance with proper initialization
            api_handler = handler(None, None, None)
            
            # Mock the response methods
            response_status = 200
            response_headers = {}
            
            def mock_send_response(status):
                nonlocal response_status
                response_status = status
            
            def mock_send_header(name, value):
                response_headers[name] = value
            
            def mock_end_headers():
                pass
            
            api_handler.send_response = mock_send_response
            api_handler.send_header = mock_send_header
            api_handler.end_headers = mock_end_headers
            
            # Call the OPTIONS handler
            api_handler.do_OPTIONS()
            
            # Send the response
            self.send_response(response_status)
            for name, value in response_headers.items():
                self.send_header(name, value)
            self.end_headers()
        else:
            super().do_OPTIONS()

if __name__ == "__main__":
    PORT = 8001
    print(f"Starting development server on http://localhost:{PORT}")
    print("This server handles both static files and API requests.")
    print("Press Ctrl+C to stop the server.")
    
    with socketserver.TCPServer(("", PORT), DevHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")