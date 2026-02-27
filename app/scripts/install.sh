#!/bin/bash
set -e

echo "Installing the required packages..." 
source venv/Scripts/activate # if WSL -> source venv/bin/activate
pip install -r requirements.txt

echo "Done!"