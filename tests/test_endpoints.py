"""
Integration tests for the Mergington High School Activities API.
Tests cover happy paths and error scenarios for all endpoints.
"""
import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint."""

    def test_get_all_activities_success(self, client):
        """Test retrieving all activities returns data successfully."""
        response = client.get("/activities")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response is a dict with expected activities
        assert isinstance(data, dict)
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data

    def test_get_activities_contains_required_fields(self, client):
        """Test that each activity has required fields."""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_data in data.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)

    def test_get_activities_participants_count_correct(self, client):
        """Test that participant count matches the list."""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_data in data.items():
            participants_count = len(activity_data["participants"])
            assert participants_count <= activity_data["max_participants"]


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint."""

    def test_signup_new_participant_success(self, client):
        """Test successfully signing up a new participant."""
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "newtudent@mergington.edu"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Signed up" in data["message"]

    def test_signup_new_participant_added_to_list(self, client):
        """Test that new participant is added to activity participants list."""
        email = "alice@mergington.edu"
        
        # Sign up the participant
        response = client.post(
            "/activities/Gym Class/signup",
            params={"email": email}
        )
        assert response.status_code == 200
        
        # Verify participant was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email in activities_data["Gym Class"]["participants"]

    def test_signup_duplicate_participant_fails(self, client):
        """Test that signing up an already registered participant fails."""
        # Michael is already signed up for Chess Club
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "michael@mergington.edu"}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"].lower()

    def test_signup_invalid_activity_fails(self, client):
        """Test that signing up for a non-existent activity fails."""
        response = client.post(
            "/activities/NonExistent Club/signup",
            params={"email": "student@mergington.edu"}
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()

    def test_signup_multiple_activities_same_student(self, client):
        """Test that a student can sign up for multiple different activities."""
        email = "versatile@mergington.edu"
        
        # Sign up for first activity
        response1 = client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        # Sign up for second activity
        response2 = client.post(
            "/activities/Programming Class/signup",
            params={"email": email}
        )
        assert response2.status_code == 200
        
        # Verify student is in both activities
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email in activities_data["Chess Club"]["participants"]
        assert email in activities_data["Programming Class"]["participants"]


class TestRemoveParticipant:
    """Tests for DELETE /activities/{activity_name}/participants/{email} endpoint."""

    def test_remove_participant_success(self, client):
        """Test successfully removing an existing participant."""
        response = client.delete(
            "/activities/Chess Club/participants/michael@mergington.edu"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Removed" in data["message"]

    def test_remove_participant_actually_removed(self, client):
        """Test that participant is actually removed from the activity."""
        email = "daniel@mergington.edu"
        
        # Remove the participant
        response = client.delete(
            f"/activities/Chess Club/participants/{email}"
        )
        assert response.status_code == 200
        
        # Verify participant was removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email not in activities_data["Chess Club"]["participants"]

    def test_remove_nonexistent_participant_fails(self, client):
        """Test that removing a participant not in activity fails."""
        response = client.delete(
            "/activities/Chess Club/participants/notmember@mergington.edu"
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()

    def test_remove_from_invalid_activity_fails(self, client):
        """Test that removing from non-existent activity fails."""
        response = client.delete(
            "/activities/NonExistent Club/participants/student@mergington.edu"
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()

    def test_remove_multiple_participants(self, client):
        """Test removing multiple different participants."""
        activity = "Gym Class"
        email1 = "john@mergington.edu"
        email2 = "olivia@mergington.edu"
        
        # Remove first participant
        response1 = client.delete(
            f"/activities/{activity}/participants/{email1}"
        )
        assert response1.status_code == 200
        
        # Remove second participant
        response2 = client.delete(
            f"/activities/{activity}/participants/{email2}"
        )
        assert response2.status_code == 200
        
        # Verify both are removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email1 not in activities_data[activity]["participants"]
        assert email2 not in activities_data[activity]["participants"]


class TestIntegrationScenarios:
    """Integration tests combining multiple operations."""

    def test_signup_then_remove_participant(self, client):
        """Test signing up and then removing the same participant."""
        email = "testuser@mergington.edu"
        activity = "Chess Club"
        
        # Sign up
        signup_response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        assert signup_response.status_code == 200
        
        # Verify signup
        check_response = client.get("/activities")
        assert email in check_response.json()[activity]["participants"]
        
        # Remove
        remove_response = client.delete(
            f"/activities/{activity}/participants/{email}"
        )
        assert remove_response.status_code == 200
        
        # Verify removal
        final_response = client.get("/activities")
        assert email not in final_response.json()[activity]["participants"]

    def test_cannot_signup_after_being_removed(self, client):
        """Test signing up after being removed is allowed (fresh signup)."""
        email = "returning@mergington.edu"
        activity = "Programming Class"
        
        # First signup
        response1 = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        # Remove
        client.delete(
            f"/activities/{activity}/participants/{email}"
        )
        
        # Second signup should succeed (no longer in list)
        response2 = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        assert response2.status_code == 200

    def test_email_case_sensitivity(self, client):
        """Test that email handling is case-sensitive."""
        email_lower = "newstudent@mergington.edu"
        email_upper = "NEWSTUDENT@MERGINGTON.EDU"
        
        # Sign up with lowercase
        response1 = client.post(
            "/activities/Chess Club/signup",
            params={"email": email_lower}
        )
        assert response1.status_code == 200
        
        # Try to sign up with uppercase (should succeed as different email)
        response2 = client.post(
            "/activities/Chess Club/signup",
            params={"email": email_upper}
        )
        # This tests current behavior; adjust assertion if case-insensitive behavior is preferred
        assert response2.status_code == 200
