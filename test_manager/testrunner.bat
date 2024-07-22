@echo off

set /p fname=Enter the feature file name:
  set /p language1=Enter Language1 Under Test [python/java/rust]:
  set /p transport1=Enter Transport1 Under Test [socket/zenoh/someip]:
  set /p language2=Enter Language2 Under Test [python/java/rust/_blank_]:
  set /p transport2=Enter Transport2 Under Test [socket/zenoh/someip]:

    REM Run Behave with HTML formatter
    python -m behave --define uE1=%language1% --define uE2=%language2% --define transport1=%transport1% --define transport2=%transport2% -i %fname% --format html --outfile reports/%fname%_%date:~10,4%%date:~4,2%%date:~7,2%_%RANDOM%.html