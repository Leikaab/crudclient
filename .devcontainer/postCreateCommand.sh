#!/bin/sh

# Reload the shell environment
. ~/.bashrc

# Check if the .env file exists
if [ -f .env ]; then
    # Export the variables from .env
    export $(grep -v '^#' .env | xargs)
fi

# set up pre-commit hooks, commented out for now
poetry run pre-commit install -t pre-commit
poetry run pre-commit install -t pre-push

# Wait until poetry is available
for i in {1..5}; do
    if command -v poetry &> /dev/null
    then
        echo "Poetry found"
        break
    else
        echo "Waiting for Poetry to be available..."
        sleep 2
    fi
done


echo "Checking poetry by direct invocation:"
if /usr/local/py-utils/bin/poetry --version &> /dev/null
then
    echo "Poetry is available and working"
    poetry config virtualenvs.create false --local
else
    echo "Poetry could not be found"
fi

# Loop through all items in the /workspace directory
for item in /workspace/*; do
    # Check if the item is the .git directory
    if [ "$(basename "$item")" != ".git" ]; then
        # Change ownership of the item (file or directory)
        chown -R vscode:vscode "$item"
    fi
done
