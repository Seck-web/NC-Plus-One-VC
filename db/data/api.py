import json
from http.server import BaseHTTPRequestHandler, HTTPServer

from connection import connect_nc_plus_one


class EventsHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path.rstrip("/") != "/events":
            self.send_error(404, "Not found")
            return

        try:
            conn = connect_nc_plus_one()
            try:
                with conn.cursor() as cur:
                    cur.execute(
                        """SELECT event_id, title, description, starts_at,
                                  ends_at, organiser_id, venue_id
                           FROM events
                           ORDER BY starts_at, event_id"""
                    )
                    columns = [column.name for column in cur.description]
                    events = [
                        {
                            key: value.isoformat() if hasattr(value, "isoformat") else value
                            for key, value in zip(columns, row)
                        }
                        for row in cur.fetchall()
                    ]
            finally:
                conn.close()
        except Exception:
            self.send_error(500, "Unable to retrieve events")
            return

        payload = json.dumps({"events": events}).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)


def main():
    import os

    server = HTTPServer((os.getenv("HOST", "127.0.0.1"), int(os.getenv("PORT", "8000"))), EventsHandler)
    print(f"Serving GET /events at http://{server.server_address[0]}:{server.server_address[1]}/events")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
