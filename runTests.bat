@echo off
SETLOCAL

:: Run Maya based tests
::
:: Edit the path to 'mayapy.exe' as needed for your Maya version.
echo Starting Maya test...
"C:\Program Files\Autodesk\Maya2017\bin\mayapy.exe" ./tests/runTests.py %*
