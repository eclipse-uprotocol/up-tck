Feature: Testing opening and closing socket (client and server) connections
Scenario Outline: To test the closing connection for a Test Agent uE
    Given "<uE1>" is connected to the Test Manager

    When "<uE1>" closes its client socket connection
    
    Then Test Manager closes server socket connection to the "<uE1>"


    Examples: 
    | uE1     |
    | python  |
    | java    |