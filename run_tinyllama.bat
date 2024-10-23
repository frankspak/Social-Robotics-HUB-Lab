@echo off
start cmd /k uvicorn display:app --host 0.0.0.0 --port 8000
timeout /t 10
start cmd /k python3 startDialogueServer.py --server tinyllama
timeout /t 10
start cmd /k python module_speechrecognition.py --pip 192.168.1.140
timeout /t 10
start cmd /k python module_dialogue.py --pip 192.168.1.140 --server tinyllama
