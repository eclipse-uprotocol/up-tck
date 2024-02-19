start python ../../dispatcher/dispatcher.py
timeout /t 1
start python ./helloworld_service.py
timeout /t 1
start python ./test_rpcclient.py