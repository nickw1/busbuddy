#!/bin/bash
# Example cron script
cd /home/user/src/busbuddy/src/siri
export PYTHONPATH=..
python3 ./siri.py >> ../../logs/siri.log
