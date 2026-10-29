import os
from pathlib import Path
import psycopg2
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")


def connect_nc_plus_one():
    return psycopg2.connect(dbname=os.getenv("PGDATABASE", "nc_plus_one"))
