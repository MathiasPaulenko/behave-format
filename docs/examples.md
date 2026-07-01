# Examples

## Login Feature

```gherkin
@auth @smoke
Feature: Login
  As a user
  I want to log in
  So that I can access the system

  Background:
    Given a database connection
    And the web server is running

  @happy
  Scenario: Successful login
    Given the user is on the login page
    When the user enters "admin" and "password"
    Then the user should be logged in
    And the dashboard should be visible
```

## Data Tables

```gherkin
Feature: Data Tables
  As a developer
  I want to use data tables
  So that I can pass structured data to steps

  Scenario: User registration with data table
    Given the following users:
      | name  | email          | age |
      | Alice | alice@test.com | 30  |
      | Bob   | bob@test.com   | 25  |
    When the system processes the registrations
    Then all users should be registered
```

## Rules (Gherkin v6)

```gherkin
@auth
Feature: User Account Management
  As a registered user
  I want to manage my account
  So that my profile stays up to date

  Background:
    Given the user is logged in

  Rule: Profile updates
    Background:
      Given the user has a profile

    Scenario: Update display name
      When the user changes their display name to "Alice"
      Then the profile should show "Alice"
```

## Scenario Outline with Examples

```gherkin
@bulk
Scenario Outline: Bulk discount for <quantity> items
  Given the cart has <quantity> items
  When the user checks out
  Then the discount should be <discount>%

  Examples:
    | quantity | discount |
    | 5        | 10       |
    | 10       | 20       |
    | 50       | 30       |
```
