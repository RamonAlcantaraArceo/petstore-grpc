Feature: Transport parity for Petstore API
  As an API operator
  I want the same behavior through direct gRPC and Envoy
  So that client integrations are consistent

  Scenario Outline: Health endpoint returns SERVING
    Given a "<transport>" client
    When I execute a health check
    Then the service reports serving

    Examples:
      | transport |
      | grpc      |
      | envoy     |

  Scenario Outline: Available pets are reachable from seeded data
    Given a "<transport>" client
    When I request available pets
    Then I receive at least one available pet

    Examples:
      | transport |
      | grpc      |
      | envoy     |
