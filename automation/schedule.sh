#!/bin/bash

while true; do
    python3 automation/single.py auto_repair
    sleep 300
    
    python3 automation/single.py rapid_resolve  
    sleep 180
    
    python3 automation/single.py multi_lang
    sleep 600
    
    python3 automation/single.py collab_dev
    sleep 240
    
    python3 automation/single.py daily_update
    sleep 3600
done
