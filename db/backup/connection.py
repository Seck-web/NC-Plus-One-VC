import psycopg
import os
from dotenv import load_dotenv

load_dotenv (".env")

#create a connection function for the database      
def connect_nc_plus_one():
    if not os.getenv("PGDATABASE"):
        raise RuntimeError("PGDATABASE not set")
    return psycopg.connect(
        dbname=os.environ.get("PGDATABASE", "nc_plus_one"))

