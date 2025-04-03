#!/bin/bash

echo "🤖 Starting FitBot deployment script..."

# Change to project directory (adjust if needed)
cd "$(dirname "$0")"

# Train the model
echo "🏋️ Training Rasa model..."
cd chatbot
rasa train
cd ..

# Find the most recent model file
echo "🔍 Finding latest model..."
latest_model=$(find chatbot/models -type f -name "*.tar.gz" | sort -r | head -n 1)
echo "📦 Using model: $latest_model"

# Start the services
echo "🚀 Starting services..."

# Start the Rasa server
echo "📡 Starting Rasa server..."
rasa run --enable-api --cors "*" --model "$latest_model" --endpoints chatbot/endpoints.yml &
RASA_PID=$!

# Wait a moment to ensure Rasa server starts
sleep 3

# Start the actions server
echo "⚡ Starting Actions server..."
cd chatbot
rasa run actions &
ACTIONS_PID=$!
cd ..

# Start the HTTP server for UI
echo "🌐 Starting web server for UI..."
cd fitbot-ui && python -m http.server 8080 &
HTTP_PID=$!

# Go back to original directory
cd ..

echo "✅ All services started!"
echo "🔗 FitBot UI available at: http://localhost:8080"
echo ""
echo "🛑 Press Ctrl+C to stop all services"

# Function to kill all started processes
cleanup() {
    echo "🛑 Stopping all services..."
    kill $RASA_PID $ACTIONS_PID $HTTP_PID 2>/dev/null
    exit 0
}

# Set trap to catch Ctrl+C
trap cleanup INT

# Keep script running
wait