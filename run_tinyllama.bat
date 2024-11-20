@echo off
set /p userInput=Please enter participant Id: 

start cmd /k python display.py --server tinyllama --userid %userInput%
timeout /t 3
start cmd /k python3 startDialogueServer.py --server tinyllama
timeout /t 3
start cmd /k python module_speechrecognition.py --pip 192.168.1.140
timeout /t 3
start cmd /k python module_dialogue.py --pip 192.168.1.140 --server tinyllama --userid %userInput%
