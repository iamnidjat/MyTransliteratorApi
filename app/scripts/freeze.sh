#!/bin/bash
set -e

echo "Filling the requirements.txt file..."
pip freeze | sort > requirements.txt

echo "Done!"
