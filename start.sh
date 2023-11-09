#!/bin/bash


# Check if the script is being sourced
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    echo "Error: You must source this script, not run it. Use: source ${0}"
    exit 1
fi

# Set the name of your virtual environment
venv_name="dns_scan"


# Create the virtual environment
python3 -m venv $venv_name


# Activate the virtual environment
source $venv_name/bin/activate

python3 -m pip install -r requirements.txt
