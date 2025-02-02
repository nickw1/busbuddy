import psycopg
import os
from dotenv import load_dotenv
from popdb import TimetableDatabase

operator_code = "PH1121126"
#date = "20240929"
date = "20241028"
routes = {
    "1": "204",
    "2": "203",
    "3": "202",
    "4": "201",
    "5": "200",
    "6": "176",
    "7": "298",
    "8": "199",
    "9": "198",
    "10": "502",
    "11/12": "197",
    "13": "503",
    "14": "504",
    "15": "505",
    "16": "196",
    "17": "302",
    "18": "195",
    "19": "506",
    "20": "507",
    "21": "562",
    "22": "561",
    "23": "528",
    "24": "529",
    "U1A/C/E": "322",
    "U2/B/C": "320",
    "U6H/C" : "323",
    "U7" : "533",
    "U8" : "534",
    "U9" : "321"
}

load_dotenv()
with  psycopg.connect(f"dbname={os.environ.get('DB_NAME')} user={os.environ.get('DB_USER')}") as conn:
    with conn.cursor() as cur:
        timetable = TimetableDatabase(cur, os.environ.get('TIMETABLE_DIR'))

        #for route in routes:
        #    print(f"Route {route}")
        #    timetable.populate(operator_code, date, routes[route])
        timetable.populate(operator_code)

        conn.commit()
