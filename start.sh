#!/bin/bash

# Create a virtual environment if it doesn't exist
if [ ! -d "url-service-env" ]; then
    python3 -m venv url-service-env
    echo "Created Python virtual environment 'url-service-env'"
fi

echo "Activating Python virtual environment..."
source url-service-env/bin/activate  
pip3 install -r requirements.txt

# Set PORT variable (default to 8080 if not provided)
PORT=${1:-8080}
export PORT

# Run the Flask application
python3 app.py