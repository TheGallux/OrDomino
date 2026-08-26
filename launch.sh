#!/bin/sh

# Launch the environment
if ! [ -d venv ]; then
    echo " === Initializaing the environment ==="

    python3 -m venv venv
    . venv/bin/activate
    pip install -r requirements.txt
else
    echo " === Environment already initialized ==="
    . venv/bin/activate
fi

echo

# Launch the code
echo " === Launching the code ==="
python src/main.py
