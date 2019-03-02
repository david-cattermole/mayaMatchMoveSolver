# Run Test Suite

After the `mmSolver` Maya module is installed and can be found by
Maya, it is recommended to run the automatic test suite to confirm 
everything is working as expected.

On Linux run:
```commandline
$ cd <project root>
$ /usr/autodesk/mayaVERSION/bin/mayapy tests/runTests.py
# We can test specific files like this:
$ /usr/autodesk/mayaVERSION/bin/mayapy tests/runTests.py tests/test/test_api/test_attribute.py
```

On Windows run:
```cmd
> CD <project root>
> "C:\Program Files\Autodesk\MayaVERSION\bin\mayapy" tests\runTests.py > tests.log
REM We can test specific files like this:
> "C:\Program Files\Autodesk\MayaVERSION\bin\mayapy" tests\runTests.py tests/test/test_api/test_attribute.py > tests.log
```

Make sure you use the same Maya version 'mayapy' for testing as you
have built ``mmSolver`` with.

On Windows, 'cmd.exe' is very slow printing text to the console,
therefore redirecting to a log file ('> file.log' below) will improve
performance of the test suite greatly.

For more information about testing, see the Testing section in
[DEVELOPER.md](https://github.com/david-cattermole/mayaMatchMoveSolver/blob/master/DEVELOPER.md).
