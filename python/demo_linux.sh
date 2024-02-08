#!/bin/bash

python dispatcher/dispatcher.py &
sleep 1
python examples/tck_interoperability/test_socket_tm.py &
sleep 1
python examples/tck_interoperability/test_socket_ta.py &