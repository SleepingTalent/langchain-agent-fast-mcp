Feature: Frontend Agent
  As a user of the chat interface
  I want to ask the AI agent questions about users and products
  So that I can get answers backed by real database data

  Background:
    Given the Streamlit app is running and connected

  Scenario: Agent lists users from the database
    When I ask the agent "list all users"
    Then the response should mention a user name

  Scenario: Agent lists products from the database
    When I ask the agent "list all products"
    Then the response should mention a product name

  Scenario: Agent searches for a specific user
    When I ask the agent "find users named Alice"
    Then the response should contain "Alice"
