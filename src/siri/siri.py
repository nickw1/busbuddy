# SIRI monitor
# Send a request e.g. every 5 minutes to track vehicles and fill in the 
# journeys database with block_refs and vehicles, so that we can figure out
# workings.
# Later this will run more frequently to allow live vehicle tracking.
# designed to run as a cron job
from bods_client.client import BODSClient
from bods_client.models import BoundingBox, GTFSRTParams, Siri, SIRIVMParams, TimetableParams, Timetable
import datetime
import psycopg
import os
from dotenv import load_dotenv
from bodsdao import journey # setup PYTHONPATH to ..

load_dotenv()

bods = BODSClient(api_key=os.environ.get('API_KEY'))

bbox = { 
    "min_latitude" : 50.88,
    "max_latitude" : 50.95,
    "min_longitude" : -1.5,
    "max_longitude" : -1.3 
}

print(bbox)
bounding_box = BoundingBox(**bbox)


params2 = SIRIVMParams(bounding_box=bounding_box)
siri_response = bods.get_siri_vm_data_feed(params=params2)
siri = Siri.from_bytes(siri_response)


with psycopg.connect(f"dbname={os.environ.get('DB_NAME')} user={os.environ.get('DB_USER')}") as conn: 
    with conn.cursor() as cur:
        dao = journey.JourneyDao(cur)
        print(f"\n\nSIRI:\n=====\n\n")

        cur_day_of_week = datetime.date.today().strftime("%A")[0:2]

        for activity in siri.service_delivery.vehicle_monitoring_delivery.vehicle_activities:
            time = activity.monitored_vehicle_journey.origin_aimed_departure_time.time()
            if time is None:
                print(f"Ignoring record with no departure time")
            else:
                # Find in DB the corresponding journey record
                # populate its block_ref and vehicle_ref
                # another tool (running daily) will then analyse the block_refs for consistency
                # vehicle_ref is provided for backup in case block_ref is not present
                journey = dao.find_journey(
                    cur_day_of_week, 
                    #time.strftime("%H:%M:00"), 
                    time,
                    activity.monitored_vehicle_journey.published_line_name, 
                    activity.monitored_vehicle_journey.direction_ref
                )
                print(f"""
Journey id for {cur_day_of_week} at {time} on route {activity.monitored_vehicle_journey.published_line_name} 
direction {activity.monitored_vehicle_journey.direction_ref} = {journey} 
                """)
                if journey is not None:
                    n_updated = dao.update_journey(
                        journey, 
                        activity.monitored_vehicle_journey.block_ref, 
                        activity.monitored_vehicle_journey.vehicle_ref
                    )
                    print(f"Updated {n_updated} journeys.")
