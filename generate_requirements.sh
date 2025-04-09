#!/bin/bash

############################################################################
# Generate requirements.txt from requirements.in
############################################################################

echo "Generating requirements.txt"

CURR_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

pip install -r ${CURR_DIR}/requirements.in
pip freeze > ${CURR_DIR}/requirements.txt
