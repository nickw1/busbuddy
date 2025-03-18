import psycopg
import os
import sys
from dotenv import load_dotenv
from timetable_database import TimetableDatabase

load_dotenv()
with  psycopg.connect(f"dbname={os.environ.get('DB_NAME')} user={os.environ.get('DB_USER')}") as conn:
    with conn.cursor() as cur:
        timetable_dir = os.environ.get('TIMETABLE_DIR')
        if timetable_dir is None:
            print("Please set the TIMETABLE_DIR environment variable to point to your timetable directory.")
        elif len(sys.argv) < 4:
            print(f"Usage: python3 {sys.argv[0]} operator_code dataset_id date")
        else:
            timetable = TimetableDatabase(cur, timetable_dir)
            timetable.populate(sys.argv[1], sys.argv[2], sys.argv[3])
            conn.commit()
