# SIRI monitor
# Send a request repeatedly to track vehicles and fill in the 
# journeys database with block_refs and vehicles, so that we can figure out
# workings.
# Use with cron or similar.
from bods_client.client import BODSClient
from bods_client.models import BoundingBox, SIRIVMParams, Siri
import datetime
import psycopg
import os
from dotenv import load_dotenv
from bodsdao import journey # set PYTHONPATH to ..

load_dotenv()

bods = BODSClient(api_key=os.environ.get('API_KEY'))

bbox = { 
    "min_latitude" : 50.88,
    "max_latitude" : 50.95,
    "min_longitude" : -1.5,
    "max_longitude" : -1.3 
}

bounding_box = BoundingBox(**bbox)
siri_params = SIRIVMParams(bounding_box=bounding_box)


try:
    siri_response = bods.get_siri_vm_data_feed(params=siri_params)
    siri = Siri.from_bytes(siri_response)
    with psycopg.connect(f"dbname={os.environ.get('DB_NAME')} user={os.environ.get('DB_USER')}") as conn: 
        with conn.cursor() as cur:
            dao = journey.JourneyDao(cur)
            print(f"\n\nSIRI:\n=====\n\n")

            cur_day_of_week = datetime.date.today().strftime("%A")[0:2]

            for activity in siri.service_delivery.vehicle_monitoring_delivery.vehicle_activities:
                deptime = activity.monitored_vehicle_journey.origin_aimed_departure_time
                if deptime is None:
                    print(f"Ignoring record with no departure time")
                else:
                    # Find in DB the corresponding journey record
                    # populate its block_ref and vehicle_ref
                    # another tool (running daily) will then dump a day's 
                    # records in another table and analyse the block_refs for 
                    # consistency
                    # vehicle_ref is provided for backup in case block_ref is 
                    # not present
                    time = deptime.time()
                    journey = dao.find_journey(
                        cur_day_of_week, 
                        time,
                        activity.monitored_vehicle_journey.published_line_name, 
                        activity.monitored_vehicle_journey.direction_ref
                    )
                    print(f"""
{cur_day_of_week} at {time} on route {activity.monitored_vehicle_journey.published_line_name} direction {activity.monitored_vehicle_journey.direction_ref}:
journey id={journey}
                    """)
                    if journey is not None:
                        n_updated = dao.update_journey(
                            journey, 
                            activity.monitored_vehicle_journey.block_ref, 
                            activity.monitored_vehicle_journey.vehicle_ref
                        )
                        print(f"Updated {n_updated} journeys.")
                    else:
                        print("Ignoring as cannot find this journey in the database.")
except Exception as e:
    print(e)
