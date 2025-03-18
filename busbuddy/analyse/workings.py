import psycopg
import os
import dotenv
import sys
from psycopg.rows import dict_row

dotenv.load_dotenv()

workings={}
freqs={}
dates=set()
if len(sys.argv) < 3:
    print(f"Usage: python3 {sys.argv[0]} startdate enddate")
    sys.exit(1)

startdate=sys.argv[1]
enddate=sys.argv[2]

with psycopg.connect(f"dbname={os.environ.get('DB_NAME')} user={os.environ.get('DB_USER')}", row_factory=dict_row) as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT j.route, j.deptime, j.direction, j.block_ref, log.journeyid, d.date, log.vehicle_today FROM daily_journey_log log INNER JOIN dates d ON d.id=log.dateid INNER JOIN journeys j ON j.id=log.journeyid WHERE extract(dow from d.date::timestamp) BETWEEN 1 AND 5 AND d.date BETWEEN %s AND %s ORDER BY log.dateid, log.vehicle_today, j.deptime", (startdate, enddate))
        results = cur.fetchall()
        last_vehicle = None
        key = None
        for result in results: 
            date = result["date"].isoformat()
            dates.add(date)
            if last_vehicle != result["vehicle_today"]:
                #key = f"{result['route']}:{result['deptime'].hour*120+result['deptime'].minute*2+(1 if result['direction'][0] == 'i' else 0)}"
                key = f"{result['block_ref'] if result['block_ref'] is not None else result['route']}:{result['journeyid']}"
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

        threshold=0.5
        counted={}
        print(f"Number of dates: {len(dates)}")
        ndates = len(dates)
        if ndates < 5:
            print("Error: a minimum of 5 dates is required.")
        else:
            for wkey in workings:
                operated_dates = len(workings[wkey])
                print(f"WORKING: {wkey} operated on {operated_dates} dates out of {ndates}.")
                if operated_dates / ndates >= threshold:         
                    print("*** Counting ***")
                    for date in workings[wkey]:
                        print(f"Date {date}: Vehicle {workings[wkey][date]['vehicle']}")
                        for journey in workings[wkey][date]["journeys"]:
                            freqs[wkey][journey['journeyid']] = 1 if journey['journeyid'] not in freqs[wkey] else freqs[wkey][journey['journeyid']] + 1

            for fkey in freqs:
                for journeyid in freqs[fkey]:
                    if freqs[fkey][journeyid] / ndates >= threshold:
                        if fkey not in counted:
                            counted[fkey] = []
                        counted[fkey].append(journeyid)

        print("***** COUNTED WORKINGS *****")
        for working in counted:
            print(f"{working} {counted[working]}")
            for journey in counted[working]:
                cur.execute("UPDATE journeys SET analysed_block_ref=%s WHERE id=%s",(working, journey))
