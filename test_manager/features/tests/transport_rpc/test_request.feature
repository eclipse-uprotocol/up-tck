Feature: Testing Publish and Subscribe Functionality

  Scenario Outline: To test the registerlistener and send apis
    Given "<uE1>" creates data for "registerlistener"
    And sets "entity.name" to "body.access"
    And sets "resource.name" to "door"
    And sets "resource.instance" to "front_left"
    And sets "resource.message" to "Door"

    When sends "registerlistener" request

    Then the status received with "code" is "OK"

    Examples:
      | uE1    | uE2    |
      | python | python |
