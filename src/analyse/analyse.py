
import psycopg
import dotenv
import os

dotenv.load_dotenv()

try:
    with psycopg.connect(f"user={os.environ.get('DB_USER')} dbname={os.environ.get('DB_NAME')}") as conn:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO dates(date) VALUES (current_date) RETURNING id")
            date_id = int(cur.fetchone()[0])
            print(date_id)
            cur.execute("INSERT INTO daily_journey_log SELECT  j.id AS journeyid, j.block_ref, j.vehicle_today, d.id as dateid FROM journeys j, dates d WHERE d.id=%s AND (j.vehicle_today IS NOT NULL OR j.block_ref IS NOT NULL) ORDER BY j.vehicle_today, j.deptime", [date_id])
            cur.execute("UPDATE journeys SET block_ref=NULL, vehicle_today=NULL");
            conn.commit()
except Exception as e:
    print(e)
