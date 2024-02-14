Feature: Default
Scenario Outline: To test the registerlistener and send apis
    Given “uE1” creates data for "registerlistener"
      And sets "uri.entity.name" to "body.access"
      And sets "uri.resource.name" to "door"
      And sets "uri.resource.instance" to "front_left"
      And sets "uri.resource.message" to "Door"
      And sends "registerlistener" request

    When “uE2” creates data for "send"
      And sets "uri.entity.name" to "body.access"
      And sets "uri.resource.name" to "door"
      And sets "uri.resource.instance" to "front_left"
      And sets "uri.resource.message" to "Door"
      And sets "attributes.priority" to "UPRIORITY_CS1"
      And sets "attributes.type" to "UMESSAGE_TYPE_PUBLISH"
      And sets "attributes.id" to "long serialized uuid"
      And sets "payload.format" to "UPAYLOAD_FORMAT_PROTOBUF"
      And sets "payload.value" to "serialized protobuf data"
      And sends "send" request

    Then uE1 receives the payload

    Examples: topic_names
    | uE1     | uE2    |
    | python  | python |