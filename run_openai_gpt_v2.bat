@echo off
set /p userInput=Please enter participant Id: 

start cmd /k python display_2_0.py --server openai --userid %userInput%
timeout /t 3
start cmd /k python3 startDialogueServer.py --server openai
timeout /t 3
start cmd /k python module_speechrecognition.py --pip 192.168.1.140
timeout /t 3
start cmd /k python module_dialogue.py --pip 192.168.1.140 --server openai --userid %userInput%