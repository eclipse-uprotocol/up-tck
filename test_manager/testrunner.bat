@echo off

set /p fname=Enter the feature file name:

    REM Run Behave with HTML formatter
    python -m behave -i %fname% --format html --outfile reports/%fname%_%date:~10,4%%date:~4,2%%date:~7,2%_%RANDOM%.html