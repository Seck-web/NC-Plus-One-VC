import psycopg2
import os
import json
from pathlib import Path


#create a function to read the json files
def _read_json(data_dir, filename):
    path = Path(data_dir) / filename
    with path.open(encoding="utf-8") as data_file:
        return json.load(data_file)

#create a seed function for the database using the json files provided to auto populate
def seed_nc_plus_one(conn, data_dir=None):

    drop_users = "DROP TABLE IF EXISTS users;"    

    create_users = """
            CREATE TABLE users (
                id SERIAL PRIMARY KEY,
                email  VARCHAR(255) NOT NULL,
                password VARCHAR(255) NOT NULL,
                name VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT());
                """

    insert_users = """
            INSERT INTO users
            (email, password, name)
            VALUES
            (%s, %s, %s)
            """

    create_venues = """
            CREATE TABLE venues(
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            address VARCHAR(255) NOT NULL,
            capacity INT NOT NULL);
            """

    create_rsvps = """
            CREATE TABLE rsvps (
            attendee_id SERIAL PRIMARY KEY,
            event_id INT NOT NULL);
            """


    with conn.cursor() as cur:
        cur.execute(drop_users)
        cur.execute(create_users)
        cur.execute(insert_users)
        cur.execute(create_venues)
        cur.execute(create_rsvps)
        cur.executemany(insert_users, [(u["email"], u["password"], u["name"])for u in users])

    conn.commit()
    
    cursor = conn.cursor()
    users = _read_json(data_dir, "users.json")
    venues = _read_json(data_dir, "venues.json")
    events = _read_json(data_dir, "events.json")
    rsvps = _read_json(data_dir, "rsvps.json")

    for venue_id, venue in enumerate(venues, start=1):
                cursor.execute(
                    """INSERT INTO venues (venue_id, name, address, capacity)
                       VALUES (%s, %s, %s, %s)
                       ON CONFLICT (venue_id) DO UPDATE SET
                           name = EXCLUDED.name,
                           address = EXCLUDED.address,
                           capacity = EXCLUDED.capacity""",
                    (venue_id, venue["name"], venue["address"], venue["capacity"]),
                )

    conn.commit()

    for event_id, event in enumerate(events, start=1):
                cursor.execute(
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
                    (
                        event_id,
                        event["title"],
                        event["description"],
                        event["starts_at"],
                        event["ends_at"],
                        event["organiser_id"],
                        event["venue_id"],
                    ),
    conn.commit()

                )
    for rsvp in rsvps:
           cursor.execute(
                """INSERT INTO rsvps (attendee_id, event_id)
                  SELECT %s, %s
                  WHERE NOT EXISTS (
                    SELECT 1 FROM rsvps
                    WHERE attendee_id = %s AND event_id = %s
                )""",
            (
                   rsvp["attendee_id"],
                   rsvp["event_id"],
            ),
           )
    conn.commit()

    for table, column in (
                ("users", "user_id"),
                ("venues", "venue_id"),
                ("events", "event_id"),
            ):
            cursor.execute(
                "SELECT setval(pg_get_serial_sequence(%s, %s), "
                f"GREATEST(COALESCE((SELECT MAX({column}) FROM {table}), 1), 1), true)",
                (table, column),
            )

    return {
        "users": len(users),
        "venues": len(venues),
        "events": len(events),
        "rsvps": len(rsvps),
            }




# def main():
#     with connect_nc_plus_one() as conn:
#         print(seed_nc_plus_one(conn))


# if __name__ == "__main__":
#     main()