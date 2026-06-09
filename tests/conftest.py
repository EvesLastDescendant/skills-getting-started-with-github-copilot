"""
Pytest configuration and fixtures for FastAPI tests.
"""
import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset the activities database before each test."""
    # Store original data
    original_data = {
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
        "Basketball Team": {
            "description": "Practice team drills and compete in interschool basketball games",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 18,
            "participants": ["tyler@mergington.edu", "nina@mergington.edu"]
        },
        "Swimming Club": {
            "description": "Build swimming skills and improve aquatic fitness",
            "schedule": "Tuesdays and Thursdays, 5:00 PM - 6:30 PM",
            "max_participants": 25,
            "participants": ["mia@mergington.edu", "ryan@mergington.edu"]
        },
        "Art Club": {
            "description": "Explore drawing, painting, and mixed media art projects",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": ["zoe@mergington.edu", "harper@mergington.edu"]
        },
        "Music Ensemble": {
            "description": "Rehearse songs and perform as a group in school concerts",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 24,
            "participants": ["leo@mergington.edu", "ava@mergington.edu"]
        },
        "Debate Society": {
            "description": "Practice public speaking, argumentation, and competitive debates",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 16,
            "participants": ["sophia@mergington.edu", "mason@mergington.edu"]
        },
        "Science Club": {
            "description": "Conduct experiments and explore scientific concepts together",
            "schedule": "Tuesdays, 4:00 PM - 5:30 PM",
            "max_participants": 22,
            "participants": ["noah@mergington.edu", "lily@mergington.edu"]
        }
    }

    # Clear and reset activities
    activities.clear()
    activities.update(original_data)

    yield

    # Clean up after test
    activities.clear()
    activities.update(original_data)
