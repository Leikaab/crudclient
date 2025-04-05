#!/bin/bash

echo "Checking if Chrome is running on the host machine with remote debugging enabled..."

# Try to connect to Chrome DevTools Protocol
if curl -s http://localhost:9222/json/version > /dev/null; then
    echo "✅ Successfully connected to Chrome on the host machine!"
    echo "Chrome DevTools Protocol details:"
    if command -v jq &> /dev/null; then
        curl -s http://localhost:9222/json/version | jq .
    else
        curl -s http://localhost:9222/json/version
    fi
else
    echo "❌ Could not connect to Chrome on the host machine."
    echo ""
    echo "Please make sure Chrome is running on your host machine with remote debugging enabled:"
    echo ""
    echo "Windows:"
    echo "\"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe\" --remote-debugging-port=9222"
    echo ""
    echo "macOS:"
    echo "/Applications/Google\\ Chrome.app/Contents/MacOS/Google\\ Chrome --remote-debugging-port=9222"
    echo ""
    echo "Linux:"
    echo "google-chrome --remote-debugging-port=9222"
    echo ""
    echo "See REMOTE_BROWSER_SETUP.md for more details."
fi