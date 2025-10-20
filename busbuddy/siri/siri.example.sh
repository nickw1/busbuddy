#!/bin/bash
# Example cron script
cd /home/user/src/busbuddy/busbuddy/siri
export PYTHONPATH=../..
python3 ./siri.py >> ../../logs/siri.log
