@echo off

set /p fname=Enter the feature file name:
  set /p language=Enter Language Under Test [python/java]:
    set /p transport=Enter Transport Under Test [socket]:

    REM Run Behave with HTML formatter
    python -m behave --define uE1=%language% --define transport=%transport% -i %fname% --format html --outfile reports/%fname%_%date:~10,4%%date:~4,2%%date:~7,2%_%RANDOM%.html