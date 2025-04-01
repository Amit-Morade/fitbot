from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import requests
import random
import re
import textwrap
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Muscle mapping for WGER API
MUSCLE_MAP = {
    "legs": "10", 
    "arms": "5", 
    "chest": "4", 
    "back": "12", 
    "core": "6", 
    "cardio": "7"
}

# Goal to category mapping for WGER API
GOAL_CATEGORY_MAP = {
    "weight_loss": [4, 10],  # Abs and Cardio
    "muscle_gain": [8],      # Arms
    "endurance": [10, 4, 14] # Cardio, Abs, Calves
}

# Fallback workout responses when API fails
HOME_WORKOUTS = [
    "Try 3 rounds of 20 squats, 10 push-ups, and 30-sec planks!",
    "Bodyweight circuit: lunges, jumping jacks, and sit-ups (x3 sets).",
    "Home HIIT: squats, mountain climbers, burpees — 40s on, 20s off!"
]

LEG_ROUTINES = [
    "Leg day: Squats, lunges, deadlifts, calf raises — 3x10 each!",
    "Power legs: Bulgarian split squats, jump squats, wall sit.",
    "Lower body blast: goblet squats, step-ups, hamstring curls."
]

FULL_BODY = [
    "Burpees, push-ups, planks, and jump squats — full-body fire!",
    "1 min each: jumping jacks, squats, push-ups, crunches (3 rounds).",
    "Full-body circuit: mountain climbers, lunges, high knees, sit-ups!"
]

class ActionRecommendWorkout(Action):
    def name(self) -> Text:
        return "action_recommend_workout"

    def run(self, 
           dispatcher: CollectingDispatcher,
           tracker: Tracker,
           domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Get slot values
        equipment = tracker.get_slot("equipment")
        duration = tracker.get_slot("duration")
        muscle_group = tracker.get_slot("muscle_group")
        fitness_goal = tracker.get_slot("fitness_goal")
        
        # Determine workout type from intent
        intent = tracker.latest_message.get("intent", {}).get("name", "")
        workout_type = "home"  # default
        
        if intent == "ask_leg_day_routine":
            workout_type = "leg_day"
            if not muscle_group:
                muscle_group = "legs"
        elif intent == "ask_full_body_workout":
            workout_type = "full_body"
        
        # If slots are missing, use defaults
        if not equipment:
            equipment = "bodyweight"
        
        if not duration:
            duration = "30"
        
        try:
            # If we have a muscle group, fetch exercises for that muscle
            if muscle_group and muscle_group in MUSCLE_MAP:
                exercises = self.fetch_exercises_by_muscle(muscle_group)
                response = self.format_muscle_response(exercises, muscle_group, equipment, duration)
            
            # If we have a fitness goal, fetch exercises for that goal
            elif fitness_goal and fitness_goal in GOAL_CATEGORY_MAP:
                exercises = self.fetch_exercises_by_goal(fitness_goal)
                response = self.format_goal_response(exercises, fitness_goal, equipment, duration)
            
            # Otherwise determine by workout type
            elif workout_type == "leg_day":
                exercises = self.fetch_exercises_by_muscle("legs")
                response = self.format_muscle_response(exercises, "legs", equipment, duration)
            
            elif workout_type == "full_body":
                # For full body, get a mix of exercises
                muscles = ["chest", "back", "legs", "arms", "core"]
                all_exercises = []
                
                # Get one exercise from each muscle group
                for muscle in muscles:
                    muscle_exercises = self.fetch_exercises_by_muscle(muscle)
                    if muscle_exercises and not muscle_exercises[0].startswith("Couldn't fetch"):
                        # Take one random exercise from each muscle group
                        all_exercises.append(random.choice(muscle_exercises))
                
                if all_exercises:
                    response = self.format_muscle_response(all_exercises, "full body", equipment, duration)
                else:
                    # Fallback to predefined full body workout
                    response = f"Here's your {duration}-Minute Full Body Workout:\n\n"
                    response += f"🔸 Duration: {duration} minutes\n"
                    response += f"🔸 Equipment: {equipment}\n"
                    response += f"🔸 Warm-up: 5 minutes of light cardio and dynamic stretching\n\n"
                    response += f"{random.choice(FULL_BODY)}\n\n"
                    response += "Remember to stay hydrated and listen to your body. Don't push through pain!"
            
            else:  # home workout
                # For home workout, get a mix of exercises or use fallback
                try:
                    muscles = ["chest", "back", "legs", "arms"]
                    all_exercises = []
                    
                    # Get exercises from various muscle groups
                    for muscle in muscles:
                        muscle_exercises = self.fetch_exercises_by_muscle(muscle)
                        if muscle_exercises and not muscle_exercises[0].startswith("Couldn't fetch"):
                            all_exercises.append(random.choice(muscle_exercises))
                    
                    if all_exercises:
                        response = self.format_muscle_response(all_exercises, "home", equipment, duration)
                    else:
                        # Fallback to predefined home workout
                        response = f"Here's your {duration}-Minute Home Workout:\n\n"
                        response += f"🔸 Duration: {duration} minutes\n"
                        response += f"🔸 Equipment: {equipment}\n"
                        response += f"🔸 Warm-up: 5 minutes of light cardio and dynamic stretching\n\n"
                        response += f"{random.choice(HOME_WORKOUTS)}\n\n"
                        response += "Remember to stay hydrated and listen to your body. Don't push through pain!"
                except Exception as e:
                    logger.error(f"Error generating home workout: {e}")
                    response = f"Here's your {duration}-Minute Home Workout:\n\n"
                    response += f"🔸 Duration: {duration} minutes\n"
                    response += f"🔸 Equipment: {equipment}\n"
                    response += f"🔸 Warm-up: 5 minutes of light cardio and dynamic stretching\n\n"
                    response += f"{random.choice(HOME_WORKOUTS)}\n\n"
                    response += "Remember to stay hydrated and listen to your body. Don't push through pain!"
            
            dispatcher.utter_message(text=response)
            
            # Set slots for future reference
            return [
                SlotSet("workout_type", workout_type),
                SlotSet("muscle_group", muscle_group)
            ]
            
        except Exception as e:
            logger.error(f"Error generating workout: {e}")
            fallback_response = f"I'm having trouble connecting to my fitness database right now. Here's a quick {workout_type} workout instead:\n\n"
            
            if workout_type == "leg_day":
                fallback_response += random.choice(LEG_ROUTINES)
            elif workout_type == "full_body":
                fallback_response += random.choice(FULL_BODY)
            else:
                fallback_response += random.choice(HOME_WORKOUTS)
                
            dispatcher.utter_message(text=fallback_response)
            return []
    
    def fetch_exercises_by_muscle(self, muscle_name="legs"):
        """Fetch exercises from WGER API based on muscle group"""
        muscle_id = MUSCLE_MAP.get(muscle_name.lower(), "10")
        try:
            url = f"https://wger.de/api/v2/exerciseinfo/?language=2&limit=20&muscles={muscle_id}"
            res = requests.get(url)
            data = res.json()

            exercises = []
            for item in data.get("results", []):
                name = None
                desc = ""
                for t in item.get("translations", []):
                    if t.get("language") == 2:
                        name = t.get("name")
                        desc = re.sub("<[^>]+>", "", t.get("description", "")).strip()
                        break
                if name:
                    wrapped = textwrap.fill(desc, width=80)
                    entry = f"{name}: {wrapped}"
                    exercises.append(entry)

            return exercises or ["No exercises found for this muscle group."]
        except Exception as e:
            logger.error(f"API error: {e}")
            return [f"Couldn't fetch exercises right now. API error: {e}"]
    
    def fetch_exercises_by_goal(self, goal):
        """Fetch exercises from WGER API based on fitness goal"""
        categories = GOAL_CATEGORY_MAP.get(goal, [])
        exercises = []

        for cat in categories:
            try:
                url = f"https://wger.de/api/v2/exerciseinfo/?language=2&limit=20&category={cat}"
                res = requests.get(url)
                data = res.json()

                for item in data.get("results", []):
                    name = None
                    desc = ""
                    for t in item.get("translations", []):
                        if t.get("language") == 2:
                            name = t.get("name")
                            desc = re.sub("<[^>]+>", "", t.get("description", "")).strip()
                            break
                    if name:
                        wrapped = textwrap.fill(desc, width=80)
                        entry = f"{name}: {wrapped}"
                        exercises.append(entry)

            except Exception as e:
                logger.error(f"API error for category {cat}: {e}")
                exercises.append(f"Error fetching exercises for this goal. API error: {e}")

        return exercises or ["No exercises found for this fitness goal."]
    
    def format_muscle_response(self, exercises, muscle_group, equipment, duration):
        """Format the response for muscle-focused workouts"""
        # Calculate workout parameters
        exercise_count = min(5, len(exercises))
        selected_exercises = random.sample(exercises, exercise_count) if len(exercises) > exercise_count else exercises
        
        # Make workout title
        if muscle_group == "full body":
            title = f"{duration}-Minute Full Body Workout"
        elif muscle_group == "home":
            title = f"{duration}-Minute Home Workout"
        else:
            title = f"{duration}-Minute {muscle_group.capitalize()} Workout"
        
        # Build response
        response = f"Here's your {title}:\n\n"
        response += f"🔸 Duration: {duration} minutes\n"
        response += f"🔸 Equipment: {equipment}\n"
        response += f"🔸 Warm-up: 5 minutes of light cardio and dynamic stretching\n\n"
        
        # Add exercises
        for i, exercise in enumerate(selected_exercises, 1):
            # Split name and description
            parts = exercise.split(":", 1)
            name = parts[0].strip()
            desc = parts[1].strip() if len(parts) > 1 else ""
            
            # Add exercise details
            response += f"{i}. **{name}**\n"
            response += f"   • 3 sets of 12-15 reps\n"
            response += f"   • Rest: 30-60 seconds between sets\n"
            
            # Add first line of description as a tip if available
            if desc:
                first_line = desc.split("\n")[0]
                if len(first_line) > 100:
                    first_line = first_line[:97] + "..."
                response += f"   • Tip: {first_line}\n"
            
            response += "\n"
        
        response += "Remember to stay hydrated and listen to your body. Don't push through pain!"
        return response
    
    def format_goal_response(self, exercises, goal, equipment, duration):
        """Format the response for goal-focused workouts"""
        # Map goals to readable names
        goal_names = {
            "weight_loss": "Weight Loss",
            "muscle_gain": "Muscle Gain",
            "endurance": "Endurance"
        }
        
        goal_name = goal_names.get(goal, goal.replace("_", " ").title())
        
        # Calculate workout parameters
        exercise_count = min(5, len(exercises))
        selected_exercises = random.sample(exercises, exercise_count) if len(exercises) > exercise_count else exercises
        
        # Build response
        response = f"Here's your {duration}-Minute {goal_name} Workout:\n\n"
        response += f"🔸 Duration: {duration} minutes\n"
        response += f"🔸 Equipment: {equipment}\n"
        response += f"🔸 Warm-up: 5 minutes of light cardio and dynamic stretching\n\n"
        
        # Add exercises
        for i, exercise in enumerate(selected_exercises, 1):
            # Split name and description
            parts = exercise.split(":", 1)
            name = parts[0].strip()
            desc = parts[1].strip() if len(parts) > 1 else ""
            
            # Adjust reps/sets based on goal
            if goal == "weight_loss":
                sets_reps = "3 sets of 15-20 reps with minimal rest"
            elif goal == "muscle_gain":
                sets_reps = "4 sets of 8-12 reps with 60-90 seconds rest"
            elif goal == "endurance":
                sets_reps = "2 sets of 20-25 reps or 45-60 second holds"
            else:
                sets_reps = "3 sets of 12-15 reps"
            
            # Add exercise details
            response += f"{i}. **{name}**\n"
            response += f"   • {sets_reps}\n"
            
            # Add first line of description as a tip if available
            if desc:
                first_line = desc.split("\n")[0]
                if len(first_line) > 100:
                    first_line = first_line[:97] + "..."
                response += f"   • Tip: {first_line}\n"
            
            response += "\n"
        
        # Add goal-specific advice
        if goal == "weight_loss":
            response += "For weight loss, keep rest periods short and intensity high.\n"
        elif goal == "muscle_gain":
            response += "For muscle gain, focus on proper form and progressive overload.\n"
        elif goal == "endurance":
            response += "For endurance, maintain a steady pace throughout the workout.\n"
        
        response += "Remember to stay hydrated and listen to your body. Don't push through pain!"
        return response


class ActionExtractMuscleGroup(Action):
    """Custom action to extract muscle group from user message"""
    
    def name(self) -> Text:
        return "action_extract_muscle_group"
    
    def run(self, 
           dispatcher: CollectingDispatcher,
           tracker: Tracker,
           domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        text = tracker.latest_message.get("text", "").lower()
        
        # Check for muscle groups in the text
        for muscle in MUSCLE_MAP.keys():
            if muscle in text:
                return [SlotSet("muscle_group", muscle)]
        
        return []


class ActionExtractFitnessGoal(Action):
    """Custom action to extract fitness goal from user message"""
    
    def name(self) -> Text:
        return "action_extract_fitness_goal"
    
    def run(self, 
           dispatcher: CollectingDispatcher,
           tracker: Tracker,
           domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        text = tracker.latest_message.get("text", "").lower()
        
        # Check for fitness goals in the text
        if re.search(r"lose.*weight|burn.*fat|fat.*loss|weight.*loss", text):
            return [SlotSet("fitness_goal", "weight_loss")]
        elif re.search(r"gain.*muscle|build.*muscle|muscle.*gain", text):
            return [SlotSet("fitness_goal", "muscle_gain")]
        elif re.search(r"endurance|stamina|cardio", text):
            return [SlotSet("fitness_goal", "endurance")]
        
        return []