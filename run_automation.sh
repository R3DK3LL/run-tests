#!/bin/bash

if [ "$1" = "continuous" ]; then
    echo "starting continuous mode"
    python3 automation/run.py
elif [ "$1" = "schedule" ]; then
    echo "starting scheduled mode" 
    ./automation/schedule.sh
elif [ "$1" = "single" ]; then
    echo "running single cycle"
    python3 automation/single.py
else
    echo "usage: $0 [continuous|schedule|single]"
    echo "  continuous: runs every hour"
    echo "  schedule: runs on custom intervals"
    echo "  single: runs once"
fi
