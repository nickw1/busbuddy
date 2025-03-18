
def parse_run_time(time):
	seconds = 0
	if time[0:2] == "PT":
		if(time[3] == "M"):
			seconds = int(time[2])*60
		elif (time[3] == "S"):
			seconds = int(time[2])
		return seconds
	else:
		print("Invalid time format")
		return -1

