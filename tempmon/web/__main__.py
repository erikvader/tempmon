from http.server import HTTPServer, SimpleHTTPRequestHandler
import os
import json
# pylint: disable=relative-beyond-top-level
from ..db.client import get

class RequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args):
        super().__init__(*args, directory=os.path.dirname(__file__) + "/website")

    def do_POST(self):
        ctype = self.headers.get("Content-Type", None)
        length = self.headers.get("Content-Length", None)
        if ctype != "application/json; charset=UTF-8" or length is None:
            self.send_error(400)
            return

        req = json.loads(self.rfile.read(int(length)).decode("utf-8"))
        year = req.get("year", None)
        month = req.get("month", None)
        day = req.get("day", None)
        if year is None or month is None or day is None:
            self.send_error(400)
            return

        resp = get(year, month, day)
        load = json.dumps(resp).encode("utf-8")

        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=UTF-8")
        self.send_header("Content-Length", len(load))
        self.end_headers()
        self.wfile.write(load)

def main():
    with HTTPServer(("", 80), RequestHandler) as httpd:
        httpd.serve_forever()

if __name__ == "__main__":
    main()

