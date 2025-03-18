class JourneyDao:

    def __init__(self, cur):
        self.cur = cur

    def insert_journey(self, block_ref, line, operator_id, dest, dep_time, run_days, direction, rev_id):
        self.cur.execute("INSERT INTO journeys(block_ref,route,operator_name,destination,deptime,run_days,direction,rev_id) VALUES(%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id", (block_ref, line, operator_id, dest, dep_time, ",".join(run_days), direction, rev_id))
        return self.cur.fetchone()[0]

    def find_journey(self, day, time, route, direction):
        self.cur.execute("SELECT id FROM journeys WHERE run_days LIKE %s AND deptime=%s AND route=%s AND direction=%s", (f"%{day}%", time, route, direction))    
        journey = self.cur.fetchone()
        return None if journey is None else journey[0]

    def update_origin(self, id, origin):
        self.cur.execute("UPDATE journeys SET origin=%s WHERE id=%s", (origin, id))

    def update_journey(self, id, block_ref, vehicle):
        self.cur.execute("UPDATE journeys SET block_ref=%s, vehicle_today=%s WHERE id=%s AND block_ref IS NULL AND vehicle_today IS NULL", (block_ref, vehicle, id))
        return self.cur.rowcount

    def clear_today(self):
        self.cur.execute("UPDATE journeys SET block_ref=NULL, vehicle_today=NULL")
