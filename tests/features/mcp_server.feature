Feature: MCP Tool Server
  As the AI agent
  I want to call database tools via the MCP server
  So that I can answer questions about users and products

  Background:
    Given the MCP server is running

  Scenario: Available tools are discoverable
    When I request the list of available tools
    Then the response should include a tool named "list_users"
    And the response should include a tool named "list_products"

  Scenario: List users returns seeded data
    When I call the "list_users" tool with no arguments
    Then the result should contain at least 1 user
    And each user should have a "name" and "email" field

  Scenario: List products returns seeded data
    When I call the "list_products" tool with no arguments
    Then the result should contain at least 1 product
    And each product should have a "name" and "price" field

  Scenario: Search users by name finds a match
    When I call the "search_users" tool with query "Alice"
    Then the result should contain at least 1 user
    And the first user's "name" should contain "Alice"

  Scenario: Get low stock products below threshold
    When I call the "get_low_stock_products" tool with threshold 50
    Then the result should contain at least 1 product
    And each product's "stock" should be below 50
