import functools
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any, Callable, Optional, Union

from tesmart.client import TesmartClient

default_port = 8088


class DeviceNotRespondException(Exception):
    pass


class ServerHandler(BaseHTTPRequestHandler):
    def __init__(self, *args: Any, client: TesmartClient, **kwargs: Any):
        self.client = client
        super().__init__(*args, **kwargs)

    def do_GET(self) -> None:
        try:
            if self.path == '/':
                self._send_ok_response({'response': 'ok'})
            elif self.path == '/ping':
                self.call(self.client.ping)
            elif self.path == '/current':
                self.call(self.client.current)
            elif self.path == '/history':
                self.call(self.client.history)
        except DeviceNotRespondException:
            self._send_ok_response({'error': "device doesn't respond"})

    def call(self, func: Callable) -> None:
        result: Union[Optional[str], Optional[dict]] = func()
        if not result:
            raise DeviceNotRespondException
        self._send_ok_response({'response': result})

    def _send_ok_response(self, body: dict) -> None:
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(bytes(json.dumps(body, ensure_ascii=False), 'utf-8'))


def server_thread(client: TesmartClient, port: int = default_port) -> None:
    address = ('127.0.0.1', port)
    handler = functools.partial(ServerHandler, client=client)
    httpd = HTTPServer(address, handler)
    try:
        print(f'server started at {address[0]}:{address[1]}')
        print('For interrupt press Ctrl+C')
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()


def run_server(client: TesmartClient) -> None:
    server_thread(client, default_port)
