import http.server
import os
import socketserver

RAIZ = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "Frontend")
PUERTO = 8080


# Las páginas .php del frontend son HTML estático: se sirven como text/html
class Manejador(http.server.SimpleHTTPRequestHandler):
    extensions_map = {**http.server.SimpleHTTPRequestHandler.extensions_map, ".php": "text/html"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=RAIZ, **kwargs)


if __name__ == "__main__":
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.ThreadingTCPServer(("127.0.0.1", PUERTO), Manejador) as srv:
        print(f"Frontend en http://127.0.0.1:{PUERTO}/index.php  (Ctrl+C para detener)")
        srv.serve_forever()
