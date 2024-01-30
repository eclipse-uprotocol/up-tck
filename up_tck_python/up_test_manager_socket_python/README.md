How to Run Test Manager/Test Agent Example:

1. Run ```python dispatcher/dispatcher.py```
2. Run ```python test_manager/test_manager.py```
3. Run ```python test_agent/test_agent.py```
    NOTE: Test Agent currently simulates Java Test Agent functionality. This will be ported to Java.
4. In test_manager, enter "java" for "SDK Language" and "registerlistener" for "Command Name".
5. After, enter "python" for "SDK Name" and "send" for command. These two commands together will test the operation of sending from a test manager to a registered test agent. Logs will go into further detail on messaging. 

TODO: Handle registerlistener response from Test Agent to Test Manager.

Next Step: Support InvokeMethod and integrate Behave Test Framework.