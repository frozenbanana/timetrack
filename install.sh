#!/bin/bash

# Define colors for output
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Build the executable
echo "Building timetrack executable..."
poetry run python build.py

# Create directory if it doesn't exist
sudo mkdir -p /usr/local/bin

# Copy the executable
echo "Installing timetrack to /usr/local/bin..."
sudo cp dist/timetrack /usr/local/bin/
sudo chmod +x /usr/local/bin/timetrack

echo -e "${GREEN}Installation complete!${NC}"
echo "You can now run 'timetrack' from anywhere."
