from connection import connect_nc_plus_one
from db import seed_nc_plus_one


def main():
    conn = connect_nc_plus_one()
    try:
        counts = seed_nc_plus_one(conn)
        print(
            f"Seeded nc_plus_one: {counts['users']} users, "
            f"{counts['venues']} venues, {counts['events']} events, "
            f"{counts['rsvps']} RSVP records."
        )
    finally:
        conn.close()


if __name__ == "__main__":
    main()
