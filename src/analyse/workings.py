import psycopg
import os
import dotenv

dotenv.load_dotenv()

with psycopg.connect(f"dbname={os.environ.get('DB_NAME')} user={os.environ.get('DB_USER')}") as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT j.route, j.deptime, j.direction, d.date, log.vehicle_today FROM daily_journey_log log INNER JOIN dates d ON d.id=log.dateid INNER JOIN journeys j ON j.id=log.journeyid WHERE extract(dow from d.date::timestamp) BETWEEN 1 AND 5 ORDER BY log.dateid, log.vehicle_today, j.deptime")
        results = cur.fetchall()
        for result in results:
            print(f"Route {result[0]} time {result[1].isoformat()} direction {result[2]} date {result[3]} vehicle {result[4]}")

        
        
