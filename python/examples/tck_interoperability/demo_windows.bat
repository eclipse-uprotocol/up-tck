start /min python ../../dispatcher/dispatcher.py
timeout /t 1
start python ./test_socket_tm.py
timeout /t 1
start /min python ./test_socket_ta.py