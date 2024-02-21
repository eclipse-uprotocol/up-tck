Feature: Default
Scenario Outline: To test the registerlistener and send apis
    Given “<uE1>” creates data for "registerlistener"
      And sets "uri.entity.name" to "body.access"
      And sets "uri.resource.name" to "door"
      And sets "uri.resource.instance" to "front_left"
      And sets "uri.resource.message" to "Door"
      And sends "registerlistener" request
      And "registerlistener" request is sent successfully

    When “<uE2>” creates data for "send"
      And sets "uri.entity.name" to "body.access"
      And sets "uri.resource.name" to "door"
      And sets "uri.resource.instance" to "front_left"
      And sets "uri.resource.message" to "Door"
      And sets "attributes.priority" to "UPRIORITY_CS1"
      And sets "attributes.type" to "UMESSAGE_TYPE_PUBLISH"
      And sets "attributes.id" to "12345"
      And sets "payload.format" to "cloudevent"
      And sets "payload.value.id" to "testme"
      And sets "payload.value.source" to "/body.access//door.front_left#Door"
      And sends "send" request
      And "send" request is sent successfully

    #Then "<uE1>" receives "payload.value" as ""

    Examples: uE used
    | uE1     | uE2    |
    | python  | java   |
    | python  | python |
    | java    | python |