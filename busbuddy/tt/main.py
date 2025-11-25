from bods_client.client import BODSClient
from bods_client.models import timetables
from bods_client.models.timetables import TimetableResponse
from datetime import datetime, date
import sys
import os
import dotenv
import argparse
import psycopg
from process_timetable import process_timetable
from timetable_database import TimetableDatabase

dotenv.load_dotenv()

tt_dir = os.environ.get("TIMETABLE_DIR") or "."
key = os.environ.get("API_KEY")
parser = argparse.ArgumentParser()
parser.add_argument('-s', '--searchterm')
parser.add_argument('-i', '--id')
parser.add_argument('-c', '--cache', action='store_true')
parser.add_argument('-d', '--startdate')
parser.add_argument('-e', '--enddate')
parser.add_argument('-n', '--nodownload', action='store_true')

datasets = []
bods = BODSClient(api_key=key)
args = parser.parse_args()

cache_dir = tt_dir if args.cache else None

if not args.nodownload:
    if args.searchterm:
        params = timetables.TimetableParams(search=args.searchterm)
        try:
            tt_response = bods.get_timetable_datasets(params=params)
        except Exception as e:
            print("Error with timetable data", file=sys.stderr)
            print(e, file=sys.stderr)
            exit(1)

        if len (tt_response.results) == 0:
            print("No results")
        else:
            print(f"Found {len(tt_response.results)} results.")
            for result in tt_response.results:
                print(f"Parsing dataset {result.id}")
                datasets.append({
                    "xmls": process_timetable(result.url, result.id, cache_dir), 
                    "modified": result.modified,
                    "dataset_id": result.id
                })
    elif args.id:
        datasets.append({
            "xmls": process_timetable(f"https://data.bus-data.dft.gov.uk/timetable/dataset/{args.id}/download/" , args.id, cache_dir), 
            "modified": datetime.now(),
            "dataset_id": args.id
        })
    else:
        print("Either a searchterm (-s) or a dataset id (-i) is required.", file=sys.stderr)
        parser.print_help()
        exit(1)
elif args.searchterm:
    print("-s option incompatible with -n; requires download")
    exit(1)

print("Importing datasets into database...")

startdate = date.fromisoformat(args.startdate) if args.startdate is not None else None
enddate = date.fromisoformat(args.enddate) if args.enddate is not None else None

with psycopg.connect(f"dbname={os.environ.get('DB_NAME')} user={os.environ.get('DB_USER')}") as conn:
    with conn.cursor() as cur:
        timetable = TimetableDatabase(cur, tt_dir)
        if len(datasets) > 0:
            for dataset in datasets:
                print(f"Importing dataset {dataset['dataset_id']}")    
                timetable.populate(raw_xmls=dataset["xmls"], modified=dataset["modified"], dataset_id=dataset["dataset_id"], start_date=startdate, end_date=enddate)
                conn.commit()
        else:
            timetable.populate(modified=datetime.now(), dataset_id=args.id, start_date=startdate, end_date=enddate)
