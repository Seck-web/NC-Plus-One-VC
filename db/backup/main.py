from db import seed_nc_plus_one
from connection import connect_nc_plus_one
import json



conn = connect_nc_plus_one

def load_json(file_path):
    with open(file_path) as f:
        return json.load(f)


seed_nc_plus_one(conn)
