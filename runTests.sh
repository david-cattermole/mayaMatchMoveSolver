#!/bin/sh

# Run Maya based tests (if 'mayapy' exists)
MAYA_PY_EXEC=mayapy
if command -v $MAYA_PY_EXEC > /dev/null; then
  echo "Starting Maya test..."
  $MAYA_PY_EXEC ./tests/runTests.py $@
fi

