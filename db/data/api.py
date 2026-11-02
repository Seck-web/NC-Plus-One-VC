import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from connection import connect_nc_plus_one
from urllib.parse import urlsplit
import os


class EventsHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        path = urlsplit(self.path).path.rstrip("/")
        if path == "/events":
            self._send_events()
            return

        parts = path.split("/")
        if len(parts) == 3 and parts[1] == "events":
            try:
                event_id = int(parts[2])
                if event_id < 1:
                    raise ValueError
            except ValueError:
                self._send_json(400, {"error": "Event ID must be a positive integer"})
                return
            self._send_event(event_id)
            return

        self._send_json(404, {"error": "Not found"})

    def _send_events(self):
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
                        self._row_to_event(columns, row)
                        for row in cur.fetchall()
                    ]
            finally:
                conn.close()
        except Exception:
            self._send_json(500, {"error": "Unable to retrieve events"})
            return

        self._send_json(200, {"events": events})

    def _send_event(self, event_id):
        try:
            conn = connect_nc_plus_one()
            try:
                with conn.cursor() as cur:
                    cur.execute(
                        """SELECT event_id, title, description, starts_at,
                                  ends_at, organiser_id, venue_id
                           FROM events
                           WHERE event_id = %s""",
                        (event_id,),
                    )
                    row = cur.fetchone()
                    if row is not None:
                        columns = [column.name for column in cur.description]
            finally:
                conn.close()
        except Exception:
            self._send_json(500, {"error": "Unable to retrieve event"})
            return

        if row is None:
            self._send_json(404, {"error": "Event not found"})
            return

        self._send_json(200, {"event": self._row_to_event(columns, row)})

    @staticmethod
    def _row_to_event(columns, row):
        return {
            key: value.isoformat() if hasattr(value, "isoformat") else value
            for key, value in zip(columns, row)
        }

    def _send_json(self, status, body):
        payload = json.dumps(body).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)


def main():

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
