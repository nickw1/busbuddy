from pathlib import Path
from datetime import date
from pytxc import Timetable
from pytxc.services import DayOfWeek
from functions import parse_run_time
from busbuddy.bodsdao import journey 
import sys
import re

class TimetableDatabase:

    def __init__(self, cur, timetable_dir):
        self.cur = cur
        self.dao = journey.JourneyDao(cur)
        self.stops = self.get_stops()
        self.day_of_week_list = list(DayOfWeek)
        self.timetable_dir = timetable_dir
        
    def populate(self, modified, dataset_id, raw_xmls=None, start_date=None, end_date=None):
        raw_xmls_provided = raw_xmls is not None 
        self.cur.execute("INSERT INTO tt_revisions(dataset_id, date) VALUES(%s,%s) RETURNING id",(int(dataset_id), modified))
        rev_id = self.cur.fetchone()[0]
        pattern = "BODS_*.xml"
        globbed = Path(f"{self.timetable_dir}/{dataset_id}").glob(pattern)
        regex = re.compile(r"BODS_\w+_\d+_(\d{4})(\d{2})(\d{2})_\d+.xml")
        for tt in raw_xmls if raw_xmls_provided else globbed:
            if tt is not None:
                if raw_xmls_provided:
                    self.timetable = Timetable.from_string(tt["xml"])
                    filename = tt["filename"]
                else: 
                    self.timetable = Timetable.from_file_path(tt)
                    filename = tt.name
                match = regex.match(filename)
                (y,m,d) = match.groups()
                tt_date = date.fromisoformat(f"{y}-{m}-{d}") 
                if (start_date is None or tt_date >= start_date) and (end_date is None or tt_date <= end_date):

                    for vj in [j for j in self.timetable.vehicle_journeys if j.operating_profile is not None]:
                        dep_time = vj.departure_time
                        block_number = vj.operational.block.block_number if vj.operational.block else None
                        jp = vj.journey_pattern_ref.resolve()
                        dest = jp.destination_display
                        direction = jp.direction
                        operator = jp.operator_ref.resolve()
                        op_prof = vj.operating_profile.days_of_week
                        line = vj.line_ref.resolve().line_name
                        run_days = [enumday.name[0:2].title() for enumday in op_prof] 
                        journey_code = vj.operational.ticket_machine.journey_code

                        journey_id=self.dao.insert_journey(block_number, line, operator.id, dest, dep_time, run_days, direction, journey_code, rev_id)
        
                        first_stop = None
                        total_run_time = 0
                        for tl in vj.timing_links:
                            timing_link = tl.journey_pattern_timing_link_ref.resolve()
                            start = timing_link.from_.stop_point_ref
                            if first_stop is None:
                                first_stop = start
                                try:
                                    self.cur.execute("INSERT INTO journeystops(journeyid,stopid,reltime) VALUES(%s,%s,0)", (journey_id, self.stops[start][0]))
                                    self.dao.update_origin(journey_id, ",".join(self.stops[start][1:]))
                                except KeyError as e:
                                    print(f"Couldn't find ATCO code {start}", file=sys.stderr)
                            end = timing_link.to.stop_point_ref
                            run_time = parse_run_time(tl.run_time) 
                            total_run_time += run_time
                            try:
                                self.cur.execute("INSERT INTO journeystops(journeyid,stopid,reltime) VALUES(%s,%s,%s)", (journey_id, self.stops[end][0], total_run_time))
                            except KeyError as e:
                                print(f"Couldn't find ATCO code {end}", file=sys.stderr)
            else:
                print(f"Could not find file {file}", file=sys.stderr)

    def get_stops(self):
        stops = {}
        self.cur.execute("SELECT atco_code, id, common_name, locality_name FROM stops")
        for row in self.cur:
            stops[row[0]] = row[1:]
        return stops
