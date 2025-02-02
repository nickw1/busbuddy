import psycopg
from dotenv import load_dotenv
import os

load_dotenv()

with psycopg.connect(f"dbname={os.environ.get('DB_NAME')} user={os.environ.get('DB_USER')}") as conn:

    with conn.cursor() as cur:

        with open('naptan.csv') as f:
            for linestr in f:
                line = linestr.rstrip().split(",")
                print(line)
                if line[-1] == "active":
                    atco_code = line[0]
                    naptan_code = line[1]    
                    common_name = line[4]
                    street = line[10]
                    locality_name = line[18]
                    parent_locality_name = line[19]
                    latitude = line[29]
                    longitude = line[30]
            
                    res = cur.execute("INSERT INTO stops(atco_code,naptan_code,common_name,street,locality_name,parent_locality_name,lon,lat) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)", (atco_code,naptan_code,common_name,street,locality_name,parent_locality_name,latitude,longitude))
        conn.commit()    
         

    
