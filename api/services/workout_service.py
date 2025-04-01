# api/services/workout_service.py
import random
from typing import Dict, List, Any

class WorkoutService:
    def __init__(self, api_key=None):
        self.api_key = api_key
        
    def create_workout(self, 
                      workout_type: str,
                      equipment: str,
                      duration: int) -> Dict[str, Any]:
        """
        Create a simple workout (placeholder until API is integrated)
        """
        # Sample exercises by type
        exercises = {
            "home": [
                "Push-ups", "Sit-ups", "Jumping Jacks", "Burpees", "Planks"
            ],
            "leg_day": [
                "Squats", "Lunges", "Calf Raises", "Glute Bridges", "Jump Squats"
            ],
            "full_body": [
                "Burpees", "Mountain Climbers", "Push-ups", "Squats", "Plank to Push-up"
            ]
        }
        
        # Get exercises for the requested type
        workout_exercises = exercises.get(workout_type, exercises["home"])
        
        # Create workout object
        workout = {
            "name": f"{duration}-Minute {workout_type.replace('_', ' ').title()} Workout",
            "duration": duration,
            "equipment": equipment,
            "warmup": "5 minutes of light cardio and dynamic stretching",
            "exercises": []
        }
        
        # Add exercises
        for exercise in workout_exercises:
            workout["exercises"].append({
                "name": exercise,
                "sets": 3,
                "reps": 12,
                "rest": "30-60 seconds between sets",
                "target": "Various muscles",
                "instructions": ["Perform with proper form", "Breathe properly throughout"]
            })
        
        return workout