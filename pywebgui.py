import json
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse


class WebGUIApp:
    def __init__(self, title: str, html: str, route_handlers: dict[str, callable] = None):
        self.title = title
        self.html = html
        self.route_handlers = route_handlers or {}

    def run(self, host: str = "127.0.0.1", port: int = 0) -> None:
        app = self

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                parsed = urlparse(self.path)
                path = parsed.path

                if path in ("/", "/index.html"):
                    self.send_response(200)
                    self.send_header("Content-Type", "text/html; charset=utf-8")
                    self.end_headers()
                    self.wfile.write(app.html.encode("utf-8"))
                    return

                if path in app.route_handlers:
                    try:
                        query = parse_qs(parsed.query)
                        result = app.route_handlers[path](query)
                        self._send_json(result)
                    except Exception as exc:
                        self.send_response(500)
                        self.send_header("Content-Type", "application/json; charset=utf-8")
                        self.end_headers()
                        self.wfile.write(json.dumps({"error": str(exc)}).encode("utf-8"))
                    return

                self.send_error(404, "Not Found")

            def _send_json(self, data):
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps(data, default=str).encode("utf-8"))

            def log_message(self, format, *args):
                # Silence default HTTP request logging
                return

        with ThreadingHTTPServer((host, port), Handler) as server:
            address = server.server_address
            url = f"http://{address[0]}:{address[1]}"
            webbrowser.open(url)
            print(f"Starting GUI at {url}")
            try:
                server.serve_forever()
            except KeyboardInterrupt:
                server.shutdown()
