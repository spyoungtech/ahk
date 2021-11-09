# Acceptance test of mouse features
Feature: Mouse functionality

  Scenario: Moving the mouse
    Given the mouse position is (100, 100)
    When I move the mouse DOWN 100px
    Then I expect the mouse position to be (100, 200)
