from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading
import socket
import os
import webbrowser
from utils.logger import logger

class AuthSuccessHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            # Servir el HTML principal
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            html_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'auth_success.html')
            with open(html_path, 'rb') as f:
                self.wfile.write(f.read())
        else:
            # Servir archivos estáticos desde la misma ubicación que el HTML
            try:
                file_path = os.path.join(os.path.dirname(__file__), '..', 'assets', self.path.lstrip('/'))
                with open(file_path, 'rb') as f:
                    self.send_response(200)
                    if file_path.endswith('.svg'):
                        self.send_header('Content-type', 'image/svg+xml')
                    elif file_path.endswith('.png'):
                        self.send_header('Content-type', 'image/png')
                    elif file_path.endswith('.jpg') or file_path.endswith('.jpeg'):
                        self.send_header('Content-type', 'image/jpeg')
                    self.end_headers()
                    self.wfile.write(f.read())
            except FileNotFoundError:
                self.send_error(404)

def get_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        s.listen(1)
        port = s.getsockname()[1]
    return port

class AuthServer:
    def __init__(self):
        self.port = get_free_port()
        self.server = HTTPServer(('localhost', self.port), AuthSuccessHandler)
        self.thread = None

    def start(self):
        self.thread = threading.Thread(target=self.server.serve_forever)
        self.thread.daemon = True
        self.thread.start()
        webbrowser.open(f'http://localhost:{self.port}')
        logger.info(f"Servidor de autenticación iniciado en puerto {self.port}")

    def stop(self):
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            logger.info("Servidor de autenticación cerrado")

# Variable global para mantener la referencia al servidor
auth_server = None

def start_success_page():
    global auth_server
    if auth_server is None:
        auth_server = AuthServer()
        auth_server.start()
    return auth_server.port

def stop_success_page():
    global auth_server
    if auth_server:
        auth_server.stop()
        auth_server = None 