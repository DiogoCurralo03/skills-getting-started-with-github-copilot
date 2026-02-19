"""
Tests for the Mergington High School API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to a known state before each test"""
    original = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        }
    }
    activities.clear()
    activities.update(original)
    yield


client = TestClient(app)


class TestGetActivities:
    def test_get_activities_returns_200(self):
        # Arrange & Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200

    def test_get_activities_returns_all_activities(self):
        # Arrange & Act
        response = client.get("/activities")
        data = response.json()

        # Assert
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data

    def test_get_activities_includes_participants(self):
        # Arrange & Act
        response = client.get("/activities")
        data = response.json()

        # Assert
        assert "michael@mergington.edu" in data["Chess Club"]["participants"]


class TestSignupForActivity:
    def test_signup_success(self):
        # Arrange
        email = "newstudent@mergington.edu"
        activity = "Chess Club"

        # Act
        response = client.post(f"/activities/{activity}/signup?email={email}")
        data = response.json()

        # Assert
        assert response.status_code == 200
        assert email in data["message"]

    def test_signup_adds_participant(self):
        # Arrange
        email = "newstudent@mergington.edu"
        activity = "Chess Club"

        # Act
        client.post(f"/activities/{activity}/signup?email={email}")

        # Assert
        assert email in activities[activity]["participants"]

    def test_signup_activity_not_found(self):
        # Arrange
        email = "student@mergington.edu"
        activity = "Nonexistent Activity"

        # Act
        response = client.post(f"/activities/{activity}/signup?email={email}")

        # Assert
        assert response.status_code == 404

    def test_signup_duplicate_student(self):
        # Arrange
        email = "michael@mergington.edu"
        activity = "Chess Club"

        # Act
        response = client.post(f"/activities/{activity}/signup?email={email}")

        # Assert
        assert response.status_code == 400

    def test_signup_activity_full(self):
        # Arrange
        activity = "Chess Club"
        # Fill the activity to max capacity
        max_participants = activities[activity]["max_participants"]
        for i in range(max_participants - len(activities[activity]["participants"])):
            activities[activity]["participants"].append(f"student{i}@mergington.edu")

        # Act
        response = client.post(f"/activities/{activity}/signup?email=overflow@mergington.edu")

        # Assert
        assert response.status_code == 400


class TestUnregisterFromActivity:
    def test_unregister_success(self):
        # Arrange
        email = "michael@mergington.edu"
        activity = "Chess Club"

        # Act
        response = client.delete(f"/activities/{activity}/signup?email={email}")
        data = response.json()

        # Assert
        assert response.status_code == 200
        assert email in data["message"]

    def test_unregister_removes_participant(self):
        # Arrange
        email = "michael@mergington.edu"
        activity = "Chess Club"

        # Act
        client.delete(f"/activities/{activity}/signup?email={email}")

        # Assert
        assert email not in activities[activity]["participants"]

    def test_unregister_activity_not_found(self):
        # Arrange
        email = "student@mergington.edu"
        activity = "Nonexistent Activity"

        # Act
        response = client.delete(f"/activities/{activity}/signup?email={email}")

        # Assert
        assert response.status_code == 404

    def test_unregister_student_not_signed_up(self):
        # Arrange
        email = "notregistered@mergington.edu"
        activity = "Chess Club"

        # Act
        response = client.delete(f"/activities/{activity}/signup?email={email}")

        # Assert
        assert response.status_code == 404
