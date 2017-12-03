#!/bin/sh

# Run Maya based tests (if 'mayapy' exists)
if command -v mayapy > /dev/null; then
  echo "Starting Maya test..."
  mayapy ./tests/runTests.py
fi

