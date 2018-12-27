@echo off
SETLOCAL

:: Run Maya based tests (if 'mayapy' exists)
echo Starting Maya test...
mayapy ./tests/runTests.py %*
