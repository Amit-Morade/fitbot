FitBot: AI-Powered Fitness Assistant
FitBot is an intelligent chatbot designed to provide personalized workout recommendations based on user preferences. Built with Rasa and integrated with the WGER API, FitBot offers customized exercise routines tailored to specific fitness goals, available equipment, and time constraints.
Show Image
Features

Personalized Workout Recommendations: Get workouts based on your fitness goals (weight loss, muscle gain, endurance)
Equipment-Aware: Customizes workouts based on available equipment (dumbbells, resistance bands, bodyweight, etc.)
Time-Efficient: Adjusts workout length based on your available time
Muscle Group Focus: Target specific muscle groups (legs, arms, chest, back, core)
Real Exercise Data: Pulls real exercises from the WGER Fitness API
Voice Input: Speak your fitness queries instead of typing

Installation
Prerequisites

Python 3.8 or higher
pip (Python package manager)
Git

Setup Instructions

Clone the repository

bashCopygit clone https://github.com/yourusername/fitbot.git
cd fitbot

Create a virtual environment

bashCopy# Create virtual environment
python -m venv venv

# Activate it (Windows)
venv\Scripts\activate

# Activate it (macOS/Linux)
source venv/bin/activate

Install dependencies

bashCopypip install -r requirements.txt

Train the Rasa model

bashCopycd chatbot
rasa train
cd ..
Running FitBot
You can run FitBot using the provided script:
bashCopychmod +x run_fitbot.sh
./run_fitbot.sh
This will:

Train the Rasa model (if needed)
Start the Rasa server
Start the Actions server
Start the web UI

Alternatively, you can start each component manually:

Start the Rasa server

bashCopyrasa run --enable-api --cors "*" --model chatbot/models/[model-name].tar.gz --endpoints chatbot/endpoints.yml

Start the Actions server (in a new terminal)

bashCopycd chatbot
rasa run actions

Start the web UI (in a new terminal)

bashCopycd fitbot-ui
python -m http.server 8080

Access the UI in your browser
Open http://localhost:8080

Project Structure
Copyfitbot/
├── api/
│   └── services/
│       ├── __init__.py
│       └── workout_service.py
├── chatbot/
│   ├── actions/
│   │   ├── __init__.py
│   │   └── actions.py
│   ├── data/
│   │   ├── nlu.yml
│   │   ├── rules.yml
│   │   └── stories.yml
│   ├── models/
│   ├── config.yml
│   ├── credentials.yml
│   ├── domain.yml
│   └── endpoints.yml
├── fitbot-ui/
│   └── index.html
├── .gitignore
├── requirements.txt
└── run_fitbot.sh
Usage Examples
Here are some examples of what you can ask FitBot:

"I need a home workout"
"Give me a leg day routine"
"I want a full body workout with dumbbells"
"I need a 30-minute workout for weight loss"
"Help me build muscle with resistance bands"
"I need to improve my endurance"
"I have dumbbells and resistance bands"

Customization
Adding New Intents
To add new intents, update the chatbot/data/nlu.yml file:
yamlCopy- intent: your_new_intent
  examples: |
    - example phrase 1
    - example phrase 2
Adding New Conversation Flows
Add new stories in chatbot/data/stories.yml:
yamlCopy- story: new_workout_path
  steps:
  - intent: your_new_intent
  - action: utter_ask_equipment
  # ... additional steps
Acknowledgments

Rasa - Open source conversational AI framework
WGER - Workout Manager API for exercise data

License
This project is licensed under the MIT License - see the LICENSE file for details.