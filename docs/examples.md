# Examples

## Login Feature

A complete login feature with background, tags, and multiple scenarios:

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

  @error
  Scenario: Failed login with wrong password
    Given the user is on the login page
    When the user enters "admin" and "wrong_password"
    Then the user should see an error message
    But the user should not be logged in
```

## Data Tables

Tables are automatically aligned with consistent column widths:

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

Gherkin v6 `Rule` keyword with nested background and scenarios:

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

    Scenario: Update email
      When the user changes their email to "alice@new.com"
      Then the profile should show "alice@new.com"
```

## Scenario Outline with Examples

Scenario outlines with examples tables are formatted with proper alignment:

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

## DocStrings

DocStrings are preserved exactly as-is:

```gherkin
Feature: API Testing
  Scenario: Create user via API
    Given the following request body:
      """json
      {
        "name": "Alice",
        "email": "alice@test.com"
      }
      """
    When the client sends a POST to "/api/users"
    Then the response should contain:
      """
      User created successfully
      """
```

## Comments

Comments are preserved in the output:

```gherkin
# Authentication feature
@auth
Feature: Login
  # Background runs before each scenario
  Background:
    Given a database connection

  # Happy path scenario
  @happy
  Scenario: Successful login
    # User enters valid credentials
    When the user enters "admin" and "password"
    Then the user should be logged in
```

## Non-English Feature

Language directives are preserved:

```gherkin
# language: es
Característica: Inicio de sesión
  Como usuario
  Quiero iniciar sesión
  Para acceder al sistema

  Escenario: Inicio de sesión exitoso
    Dado que el usuario está en la página de inicio
    Cuando el usuario ingresa "admin" y "password"
    Entonces el usuario debería estar conectado
```

## Before / After

### Before (unformatted)

```gherkin
@smoke @auth
Feature:Login
As a user
I want to log in


Background:
Given a database connection


@happy
Scenario: Successful login
Given the user is on the login page
When the user enters "admin" and "password"
Then the user should be logged in
```

### After (formatted)

```gherkin
@auth @smoke
Feature: Login
  As a user
  I want to log in

  Background:
    Given a database connection

  @happy
  Scenario: Successful login
    Given the user is on the login page
    When the user enters "admin" and "password"
    Then the user should be logged in
```

## Complex table alignment

### Before

```gherkin
|user|password|role|
|john|123|admin|
|alice|secure_pass_123|user|
|bob|456|user|
```

### After

```gherkin
    | user  | password         | role  |
    | john  | 123              | admin |
    | alice | secure_pass_123  | user  |
    | bob   | 456              | user  |
```
