#!/bin/bash

# Define colors for output
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Build and install the package globally
poetry build
pipx install --force dist/*.whl

echo -e "${GREEN}Installation complete!${NC}"