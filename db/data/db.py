"""Create and seed the NC Plus One PostgreSQL tables from JSON fixtures."""
import json
from pathlib import Path

from psycopg2 import sql

DATA_DIR = Path(__file__).resolve().parent


def _read_json(data_dir, filename):
    path = Path(data_dir) / filename
    with path.open(encoding="utf-8") as data_file:
        return json.load(data_file)


def create_tables(cur):
    cur.execute("""CREATE TABLE IF NOT EXISTS users (
        user_id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        email VARCHAR(255) UNIQUE NOT NULL,
        password VARCHAR(255) NOT NULL,
        created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
    )""")
    cur.execute("""CREATE TABLE IF NOT EXISTS venues (
        venue_id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        address TEXT,
        capacity INT NOT NULL CHECK (capacity > 0)
    )""")
    cur.execute("""CREATE TABLE IF NOT EXISTS events (
        event_id SERIAL PRIMARY KEY,
        title VARCHAR(255) UNIQUE NOT NULL,
        description TEXT,
        starts_at TIMESTAMPTZ NOT NULL,
        ends_at TIMESTAMPTZ NOT NULL,
        organiser_id INT NOT NULL REFERENCES users(user_id),
        venue_id INT NOT NULL REFERENCES venues(venue_id),
        CHECK (ends_at > starts_at)
    )""")
    cur.execute("""CREATE TABLE IF NOT EXISTS rsvps (
        attendee_id INT NOT NULL REFERENCES users(user_id),
        event_id INT NOT NULL REFERENCES events(event_id),
        PRIMARY KEY (attendee_id, event_id)
    )""")


def _set_sequence_to_max(cur, table, column):
    query = sql.SQL(
        "SELECT setval(pg_get_serial_sequence(%s, %s), "
        "GREATEST(COALESCE((SELECT MAX({column}) FROM {table}), 1), 1), true)"
    ).format(column=sql.Identifier(column), table=sql.Identifier(table))
    cur.execute(query, (table, column))


def seed_nc_plus_one(conn, data_dir=DATA_DIR):
    """Create tables and seed all fixture data in one transaction.

    Fixture order provides user, venue, and event IDs matching the references
    in events.json and rsvps.json. Existing fixture records are updated, and
    duplicate RSVP pairs are skipped. The caller closes the connection.
    """
    users = _read_json(data_dir, "users.json")
    venues = _read_json(data_dir, "venues.json")
    events = _read_json(data_dir, "events.json")
    rsvps = _read_json(data_dir, "rsvps.json")

    with conn:
        with conn.cursor() as cur:
            create_tables(cur)
            for user_id, user in enumerate(users, start=1):
                cur.execute(
                    """INSERT INTO users (user_id, name, email, password)
                       VALUES (%s, %s, %s, %s)
                       ON CONFLICT (user_id) DO UPDATE SET
                           name = EXCLUDED.name, email = EXCLUDED.email,
                           password = EXCLUDED.password""",
                    (user_id, user["name"], user["email"], user["password"]),
                )
            for venue_id, venue in enumerate(venues, start=1):
                cur.execute(
                    """INSERT INTO venues (venue_id, name, address, capacity)
                       VALUES (%s, %s, %s, %s)
                       ON CONFLICT (venue_id) DO UPDATE SET
                           name = EXCLUDED.name, address = EXCLUDED.address,
                           capacity = EXCLUDED.capacity""",
                    (venue_id, venue["name"], venue["address"], venue["capacity"]),
                )
            for event_id, event in enumerate(events, start=1):
                cur.execute(
                    """INSERT INTO events
                           (event_id, title, description, starts_at, ends_at,
                            organiser_id, venue_id)
                       VALUES (%s, %s, %s, %s, %s, %s, %s)
                       ON CONFLICT (event_id) DO UPDATE SET
                           title = EXCLUDED.title,
                           description = EXCLUDED.description,
                           starts_at = EXCLUDED.starts_at,
                           ends_at = EXCLUDED.ends_at,
                           organiser_id = EXCLUDED.organiser_id,
                           venue_id = EXCLUDED.venue_id""",
                    (event_id, event["title"], event["description"],
                     event["starts_at"], event["ends_at"],
                     event["organiser_id"], event["venue_id"]),
                )
            for rsvp in rsvps:
                cur.execute(
                    """INSERT INTO rsvps (attendee_id, event_id)
                       VALUES (%s, %s)
                       ON CONFLICT (attendee_id, event_id) DO NOTHING""",
                    (rsvp["attendee_id"], rsvp["event_id"]),
                )
            for table, column in (
                ("users", "user_id"), ("venues", "venue_id"),
                ("events", "event_id"),
            ):
                _set_sequence_to_max(cur, table, column)

    return {"users": len(users), "venues": len(venues),
            "events": len(events), "rsvps": len(rsvps)}
