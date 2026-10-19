"""Local preview, requiring Python only. Binds loopback exclusively."""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from functools import partial
import webbrowser
import urllib.request

root=Path(__file__).resolve().parent/'dist'
for port in range(8765,8785):
    try:
        server=ThreadingHTTPServer(('127.0.0.1',port),partial(SimpleHTTPRequestHandler,directory=str(root)))
        break
    except OSError:
        try:
            with urllib.request.urlopen(f'http://127.0.0.1:{port}/',timeout=1) as r:
                if b'M82' in r.read(400):
                    webbrowser.open(f'http://127.0.0.1:{port}/')
                    raise SystemExit
        except (OSError,TimeoutError):
            pass
else:
    raise SystemExit('No available local port between 8765 and 8784')
webbrowser.open(f'http://127.0.0.1:{port}/')
try:
    server.serve_forever()
except KeyboardInterrupt:
    server.server_close()
