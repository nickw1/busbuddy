import psycopg
import os
import dotenv
from psycopg.rows import dict_row

dotenv.load_dotenv()

workings={}
freqs={}
dates=set()

with psycopg.connect(f"dbname={os.environ.get('DB_NAME')} user={os.environ.get('DB_USER')}", row_factory=dict_row) as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT j.route, j.deptime, j.direction, log.journeyid, d.date, log.vehicle_today FROM daily_journey_log log INNER JOIN dates d ON d.id=log.dateid INNER JOIN journeys j ON j.id=log.journeyid WHERE extract(dow from d.date::timestamp) BETWEEN 1 AND 5 ORDER BY log.dateid, log.vehicle_today, j.deptime")
        results = cur.fetchall()
        last_vehicle = None
        key = None
        for result in results: 
            date = result["date"].isoformat()
            dates.add(date)
            if last_vehicle != result["vehicle_today"]:
                #key = f"{result['route']}:{result['deptime'].hour*120+result['deptime'].minute*2+(1 if result['direction'][0] == 'i' else 0)}"
                key = f"{result['route']}:{result['journeyid']}"
                last_vehicle = result["vehicle_today"]
                if key not in workings:
                    workings[key] = {}
                if key not in freqs:
                    freqs[key] = {}
            if date not in workings[key]:
                workings[key][date] = {
                    "vehicle": result["vehicle_today"],
                    "journeys": []
            } 
            workings[key][date]["journeys"].append(result)
               

#            print(f"{journey['journeyid']} {journey['route']} {journey['deptime']}")

counted={}
print(f"Number of dates: {len(dates)}")
ndates = len(dates)
if ndates < 5:
    print("Error: a minimum of 5 dates is required.")
else:
    for key in workings:
#    print(f"WORKING: {key}")
        for date in workings[key]:
#        print(f"Date {date}: Vehicle {workings[key][date]['vehicle']}")
            for journey in workings[key][date]["journeys"]:
                freqs[key][journey['journeyid']] = 1 if journey['journeyid'] not in freqs[key] else freqs[key][journey['journeyid']] + 1
    threshold=0.5
    for key in freqs:
        if len(freqs[key]) / ndates >= threshold:
            for journeyid in freqs[key]:
                if freqs[key][journeyid] / len(freqs[key]) >= threshold:
                    if key not in counted:
                        counted[key] = []
                    counted[key].append(journeyid)

print(counted)
