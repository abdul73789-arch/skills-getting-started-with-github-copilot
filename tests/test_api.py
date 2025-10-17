"""
Test suite for Mergington High School API endpoints
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities data before each test"""
    # Store original state
    original_activities = {
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
        },
        "Soccer Team": {
            "description": "Competitive soccer team practicing drills and playing matches",
            "schedule": "Monday, Wednesday, Friday, 4:00 PM - 6:00 PM",
            "max_participants": 18,
            "participants": ["alex@mergington.edu", "sara@mergington.edu"]
        },
        "Basketball Club": {
            "description": "Pickup games, skills training, and intramural tournaments",
            "schedule": "Tuesdays and Thursdays, 5:00 PM - 7:00 PM",
            "max_participants": 12,
            "participants": ["maria@mergington.edu", "lewis@mergington.edu"]
        },
        "Drama Club": {
            "description": "Acting, play production, and stagecraft for school performances",
            "schedule": "Wednesdays, 3:30 PM - 5:30 PM",
            "max_participants": 25,
            "participants": ["nina@mergington.edu", "carlos@mergington.edu"]
        },
        "Art Club": {
            "description": "Drawing, painting, and mixed-media projects",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": ["violet@mergington.edu", "owen@mergington.edu"]
        },
        "Debate Team": {
            "description": "Learn argumentation, public speaking, and compete in tournaments",
            "schedule": "Mondays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 16,
            "participants": ["harper@mergington.edu", "ryan@mergington.edu"]
        },
        "Robotics Club": {
            "description": "Design and build robots, participate in robotics competitions",
            "schedule": "Tuesdays, 4:00 PM - 6:00 PM",
            "max_participants": 14,
            "participants": ["maya@mergington.edu", "noah@mergington.edu"]
        }
    }
    
    # Reset activities to original state
    activities.clear()
    activities.update(original_activities)
    
    yield
    
    # Clean up after test
    activities.clear()
    activities.update(original_activities)


class TestRootEndpoint:
    """Tests for the root endpoint"""
    
    def test_root_redirects_to_static_index(self, client):
        """Test that root path redirects to static index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Tests for the GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client):
        """Test that all activities are returned"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 9
        assert "Chess Club" in data
        assert "Programming Class" in data
    
    def test_get_activities_structure(self, client):
        """Test that activities have correct structure"""
        response = client.get("/activities")
        data = response.json()
        
        chess_club = data["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert isinstance(chess_club["participants"], list)


class TestSignupForActivity:
    """Tests for the POST /activities/{activity_name}/signup endpoint"""
    
    def test_successful_signup(self, client):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Chess Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]
        
        # Verify participant was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "newstudent@mergington.edu" in activities_data["Chess Club"]["participants"]
    
    def test_signup_for_nonexistent_activity(self, client):
        """Test signup for an activity that doesn't exist"""
        response = client.post(
            "/activities/NonExistent Club/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Activity not found"
    
    def test_duplicate_signup(self, client):
        """Test that a student cannot sign up twice for the same activity"""
        email = "duplicate@mergington.edu"
        
        # First signup should succeed
        response1 = client.post(f"/activities/Chess Club/signup?email={email}")
        assert response1.status_code == 200
        
        # Second signup should fail
        response2 = client.post(f"/activities/Chess Club/signup?email={email}")
        assert response2.status_code == 400
        data = response2.json()
        assert data["detail"] == "Student is already signed up"
    
    def test_signup_when_activity_is_full(self, client):
        """Test signup when activity has reached max capacity"""
        # Fill up Chess Club (max 12 participants, currently has 2)
        for i in range(10):
            response = client.post(
                f"/activities/Chess Club/signup?email=student{i}@mergington.edu"
            )
            assert response.status_code == 200
        
        # Try to add one more (should fail)
        response = client.post(
            "/activities/Chess Club/signup?email=overflow@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert data["detail"] == "Activity is full"
    
    def test_signup_with_url_encoded_activity_name(self, client):
        """Test signup with URL-encoded activity name"""
        response = client.post(
            "/activities/Programming%20Class/signup?email=coder@mergington.edu"
        )
        assert response.status_code == 200
        
        # Verify participant was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "coder@mergington.edu" in activities_data["Programming Class"]["participants"]


class TestUnregisterFromActivity:
    """Tests for the DELETE /activities/{activity_name}/unregister endpoint"""
    
    def test_successful_unregister(self, client):
        """Test successful unregistration from an activity"""
        # First, sign up a student
        email = "test@mergington.edu"
        client.post(f"/activities/Chess Club/signup?email={email}")
        
        # Then unregister
        response = client.delete(f"/activities/Chess Club/unregister?email={email}")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert "Removed" in data["message"]
        
        # Verify participant was removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email not in activities_data["Chess Club"]["participants"]
    
    def test_unregister_from_nonexistent_activity(self, client):
        """Test unregistering from an activity that doesn't exist"""
        response = client.delete(
            "/activities/NonExistent Club/unregister?email=student@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Activity not found"
    
    def test_unregister_when_not_signed_up(self, client):
        """Test unregistering when student is not signed up for the activity"""
        response = client.delete(
            "/activities/Chess Club/unregister?email=notsignedup@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert data["detail"] == "Student is not signed up for this activity"
    
    def test_unregister_existing_participant(self, client):
        """Test unregistering an existing participant"""
        email = "michael@mergington.edu"
        
        # Verify student is initially signed up
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email in activities_data["Chess Club"]["participants"]
        
        # Unregister
        response = client.delete(f"/activities/Chess Club/unregister?email={email}")
        assert response.status_code == 200
        
        # Verify participant was removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email not in activities_data["Chess Club"]["participants"]


class TestIntegrationScenarios:
    """Integration tests for common user scenarios"""
    
    def test_signup_and_unregister_flow(self, client):
        """Test complete flow of signing up and then unregistering"""
        email = "flow@mergington.edu"
        activity = "Drama Club"
        
        # Get initial participant count
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()[activity]["participants"])
        
        # Sign up
        signup_response = client.post(f"/activities/{activity}/signup?email={email}")
        assert signup_response.status_code == 200
        
        # Verify count increased
        after_signup = client.get("/activities")
        assert len(after_signup.json()[activity]["participants"]) == initial_count + 1
        
        # Unregister
        unregister_response = client.delete(f"/activities/{activity}/unregister?email={email}")
        assert unregister_response.status_code == 200
        
        # Verify count returned to original
        after_unregister = client.get("/activities")
        assert len(after_unregister.json()[activity]["participants"]) == initial_count
    
    def test_multiple_students_same_activity(self, client):
        """Test multiple students signing up for the same activity"""
        activity = "Art Club"
        emails = [f"artist{i}@mergington.edu" for i in range(5)]
        
        for email in emails:
            response = client.post(f"/activities/{activity}/signup?email={email}")
            assert response.status_code == 200
        
        # Verify all were added
        activities_response = client.get("/activities")
        participants = activities_response.json()[activity]["participants"]
        for email in emails:
            assert email in participants
    
    def test_student_signs_up_for_multiple_activities(self, client):
        """Test a student signing up for multiple different activities"""
        email = "multitasker@mergington.edu"
        activities_to_join = ["Chess Club", "Programming Class", "Drama Club"]
        
        for activity in activities_to_join:
            response = client.post(f"/activities/{activity}/signup?email={email}")
            assert response.status_code == 200
        
        # Verify student is in all activities
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        for activity in activities_to_join:
            assert email in activities_data[activity]["participants"]
