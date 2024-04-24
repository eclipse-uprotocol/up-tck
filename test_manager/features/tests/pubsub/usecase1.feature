Feature: Testing Publish and Subscribe API
  Scenario Outline: To test the uE Subscribe and mE publish API  
    Given "<uE>" creates data for "registerlistener" 
    And sets "attributes.type" to "UMESSAGE_TYPE_PUBLISH"
    And sets "attributes.source.entity.name" to "0x1101"
    And sets "attributes.source.entity.id" to "0x1101"
    And sets "attributes.source.entity.version_major" to "0x1"
    And sets "attributes.source.entity.version_minor" to "0x0"
    And sets "attributes.source.authority.ip" to "172.17.0.1"
    And sets "attributes.source.resource.id" to "0x8101"
    And sets "attributes.source.resource.name" to "0x8101"
    And sets "attributes.source.resource.instance" to ""
    
    And sets "attributes.sink.entity.name" to "0x1101"
    And sets "attributes.sink.entity.id" to "0x1101"
    And sets "attributes.sink.entity.version_major" to "0x1"
    And sets "attributes.sink.entity.version_minor" to "0x0"
    And sets "attributes.sink.authority.ip" to "172.17.0.1"
    And sets "attributes.sink.resource.id" to "0x8101"
    And sets "attributes.sink.resource.name" to "0x8101"
    And sets "attributes.sink.resource.instance" to ""

    And sets "attributes.priority" to "UPRIORITY_CS4"

    And sets "payload.value" to "123"
    And sets "payload.format" to "UPAYLOAD_FORMAT_PROTOBUF_WRAPPED_IN_ANY"

    When sends "registerlistener" request
    And user waits "3" second
    Then the status received with "code" is "OK"
    Then triggers "usecase1ME" to "true"
    And user waits "10" second
    Then the status received with "payload" is "012345678"
    Then triggers "usecase1ME" to "false"

    

    # Given "<mE>" creates service
    # And sets "service.id" to "0x1101"
    # And sets "instance.id" to "0x0"
    # And sets "event.id" to "0x8101"
    # And sets "getmethod.id" to "0x0001"
    # And sets "setmethod.id" to "0x0002"
    # And sets "eventgroup.id" to "0x8101"
    # When sends a "service" request
    # And user waits for "2" seconds
    # Then the status received with "code" is "OK"
    # And starts the service

    Examples:
      | uE  |
      | ue1 |