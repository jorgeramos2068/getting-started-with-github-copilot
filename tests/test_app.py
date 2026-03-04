import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

class TestActivitiesAPI:
    """Test suite for the Mergington High School Activities API"""

    def test_get_activities_success(self):
        """Test successful retrieval of all activities"""
        # Arrange - No special setup needed
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) > 0  # Should have activities loaded
        
        # Check structure of first activity
        first_activity = next(iter(data.values()))
        required_keys = ["description", "schedule", "max_participants", "participants"]
        for key in required_keys:
            assert key in first_activity

    def test_signup_success(self):
        """Test successful student signup for an activity"""
        # Arrange
        test_email = "test.student@mergington.edu"
        activity_name = "Chess Club"
        
        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={test_email}")
        
        # Assert
        assert response.status_code == 200
        result = response.json()
        assert "message" in result
        assert test_email in result["message"]
        assert activity_name in result["message"]

    def test_signup_duplicate_rejection(self):
        """Test that duplicate signup is rejected"""
        # Arrange
        test_email = "duplicate.student@mergington.edu"
        activity_name = "Programming Class"
        
        # First signup
        client.post(f"/activities/{activity_name}/signup?email={test_email}")
        
        # Act - Attempt duplicate signup
        response = client.post(f"/activities/{activity_name}/signup?email={test_email}")
        
        # Assert
        assert response.status_code == 400
        result = response.json()
        assert "detail" in result
        assert "already signed up" in result["detail"].lower()

    def test_signup_nonexistent_activity(self):
        """Test signup for non-existent activity returns 404"""
        # Arrange
        test_email = "test@mergington.edu"
        nonexistent_activity = "NonExistent Club"
        
        # Act
        response = client.post(f"/activities/{nonexistent_activity}/signup?email={test_email}")
        
        # Assert
        assert response.status_code == 404
        result = response.json()
        assert "detail" in result
        assert "not found" in result["detail"].lower()

    def test_signup_capacity_limit(self):
        """Test that signup is rejected when activity reaches capacity"""
        # Arrange
        activity_name = "Tennis Club"  # Max 10 participants, currently 1
        test_emails = [f"player{i}@mergington.edu" for i in range(11)]  # More than capacity
        
        # Fill up the activity (add 9 more to reach 10)
        for i in range(9):
            client.post(f"/activities/{activity_name}/signup?email={test_emails[i]}")
        
        # Act - Try to add one more (should be rejected)
        response = client.post(f"/activities/{activity_name}/signup?email={test_emails[9]}")
        
        # Assert
        assert response.status_code == 400
        result = response.json()
        assert "detail" in result
        assert "capacity" in result["detail"].lower()

    def test_unregister_success(self):
        """Test successful student unregistration from an activity"""
        # Arrange
        test_email = "unregister.test@mergington.edu"
        activity_name = "Drama Club"
        
        # First sign up
        client.post(f"/activities/{activity_name}/signup?email={test_email}")
        
        # Act - Unregister
        response = client.delete(f"/activities/{activity_name}/signup?email={test_email}")
        
        # Assert
        assert response.status_code == 200
        result = response.json()
        assert "message" in result
        assert "unregistered" in result["message"].lower()

    def test_unregister_nonexistent_activity(self):
        """Test unregister from non-existent activity returns 404"""
        # Arrange
        test_email = "test@mergington.edu"
        nonexistent_activity = "Ghost Club"
        
        # Act
        response = client.delete(f"/activities/{nonexistent_activity}/signup?email={test_email}")
        
        # Assert
        assert response.status_code == 404
        result = response.json()
        assert "detail" in result
        assert "not found" in result["detail"].lower()

    def test_unregister_not_signed_up(self):
        """Test unregister for student not signed up returns 404"""
        # Arrange
        test_email = "notsignedup@mergington.edu"
        activity_name = "Art Studio"
        
        # Act
        response = client.delete(f"/activities/{activity_name}/signup?email={test_email}")
        
        # Assert
        assert response.status_code == 404
        result = response.json()
        assert "detail" in result
        assert "not signed up" in result["detail"].lower()

    def test_root_redirect(self):
        """Test root endpoint redirects to static index"""
        # Arrange - No special setup
        
        # Act
        response = client.get("/", follow_redirects=False)
        
        # Assert
        assert response.status_code == 307  # Temporary redirect
        assert "/static/index.html" in response.headers.get("location", "")