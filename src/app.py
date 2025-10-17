"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# In-memory activity database
activities = {
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


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    return activities


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Validate student is not already signed up
    if email in activity["participants"]:
        raise HTTPException(status_code=400, detail="Student is already signed up")

    # Check capacity
    if len(activity["participants"]) >= activity["max_participants"]:
        raise HTTPException(status_code=400, detail="Activity is full")

    # Add student
    activity["participants"].append(email)
    return {"message": f"Signed up {email} for {activity_name}"}


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str):
    """Unregister a student from an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Validate student is signed up
    if email not in activity["participants"]:
        raise HTTPException(status_code=400, detail="Student is not signed up for this activity")

    # Remove student
    activity["participants"].remove(email)
    return {"message": f"Removed {email} from {activity_name}"}