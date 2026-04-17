"""Unit tests for the High School Activities API."""

import pytest


class TestRoot:
    """Tests for the root endpoint."""

    def test_root_redirect(self, client, reset_activities):
        """Test that root endpoint redirects to /static/index.html."""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Tests for the GET /activities endpoint."""

    def test_get_activities_returns_all_activities(self, client, reset_activities):
        """Test that GET /activities returns all 9 activities."""
        response = client.get("/activities")
        assert response.status_code == 200
        
        activities = response.json()
        assert len(activities) == 9
        
        # Verify all expected activities are present
        expected_activities = [
            "Chess Club",
            "Programming Class",
            "Gym Class",
            "Basketball Team",
            "Tennis Club",
            "Art Studio",
            "Drama Club",
            "Debate Team",
            "Science Club"
        ]
        for activity_name in expected_activities:
            assert activity_name in activities

    def test_get_activities_returns_correct_structure(self, client, reset_activities):
        """Test that each activity has the correct structure."""
        response = client.get("/activities")
        activities = response.json()
        
        # Check Chess Club structure as an example
        chess_club = activities["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert isinstance(chess_club["participants"], list)

    def test_get_activities_includes_initial_participants(self, client, reset_activities):
        """Test that activities include their initial participants."""
        response = client.get("/activities")
        activities = response.json()
        
        # Chess Club should have michael and daniel
        chess_participants = activities["Chess Club"]["participants"]
        assert "michael@mergington.edu" in chess_participants
        assert "daniel@mergington.edu" in chess_participants
        assert len(chess_participants) == 2


class TestSignupForActivity:
    """Tests for the POST /activities/{activity_name}/signup endpoint."""

    def test_signup_for_activity_adds_participant(self, client, reset_activities):
        """Test that signing up adds a participant to an activity."""
        response = client.post(
            "/activities/Chess Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        
        result = response.json()
        assert "message" in result
        assert "newstudent@mergington.edu" in result["message"]
        assert "Chess Club" in result["message"]

    def test_signup_updates_participant_list(self, client, reset_activities):
        """Test that signup successfully updates the participant list."""
        # Sign up a new student
        client.post("/activities/Programming Class/signup?email=newstudent@mergington.edu")
        
        # Verify the student is now in the participant list
        response = client.get("/activities")
        activities = response.json()
        programming_participants = activities["Programming Class"]["participants"]
        assert "newstudent@mergington.edu" in programming_participants
        assert len(programming_participants) == 3  # emma, sophia + newstudent

    def test_signup_success_response_message(self, client, reset_activities):
        """Test that signup returns the correct success message."""
        email = "testuser@mergington.edu"
        activity_name = "Art Studio"
        
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        assert response.status_code == 200
        
        result = response.json()
        assert result["message"] == f"Signed up {email} for {activity_name}"


class TestUnregisterFromActivity:
    """Tests for the DELETE /activities/{activity_name}/unregister endpoint."""

    def test_unregister_removes_participant(self, client, reset_activities):
        """Test that unregister removes a participant from an activity."""
        response = client.delete(
            "/activities/Chess Club/unregister?email=michael@mergington.edu"
        )
        assert response.status_code == 200
        
        result = response.json()
        assert "message" in result
        assert "michael@mergington.edu" in result["message"]
        assert "Chess Club" in result["message"]

    def test_unregister_updates_participant_list(self, client, reset_activities):
        """Test that unregister successfully updates the participant list."""
        # Unregister a student
        client.delete(
            "/activities/Debate Team/unregister?email=noah@mergington.edu"
        )
        
        # Verify the student is no longer in the participant list
        response = client.get("/activities")
        activities = response.json()
        debate_participants = activities["Debate Team"]["participants"]
        assert "noah@mergington.edu" not in debate_participants
        assert len(debate_participants) == 0

    def test_unregister_success_response_message(self, client, reset_activities):
        """Test that unregister returns the correct success message."""
        email = "alex@mergington.edu"
        activity_name = "Tennis Club"
        
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )
        assert response.status_code == 200
        
        result = response.json()
        assert result["message"] == f"Unregistered {email} from {activity_name}"

    def test_unregister_multiple_participants_from_same_activity(self, client, reset_activities):
        """Test unregistering one participant when multiple exist."""
        # Drama Club has lucas and mia
        response = client.delete(
            "/activities/Drama Club/unregister?email=lucas@mergington.edu"
        )
        assert response.status_code == 200
        
        # Verify only lucas was removed, mia remains
        response = client.get("/activities")
        activities = response.json()
        drama_participants = activities["Drama Club"]["participants"]
        assert "lucas@mergington.edu" not in drama_participants
        assert "mia@mergington.edu" in drama_participants
        assert len(drama_participants) == 1
