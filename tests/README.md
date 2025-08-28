# Run Test Suite

After the `mmSolver` Maya module is installed and can be found by
Maya, it is recommended to run the automatic test suite to confirm 
everything is working as expected.

On Linux run:
```commandline
$ cd <project root>

# Using convenience test scripts:
$ bash scripts/test_mmSolver_linux_maya2024.bash
# We can test specific files like this:
$ bash scripts/test_mmSolver_linux_maya2024.bash tests/test/test_api/test_attribute.py
# Run all API tests:
$ bash scripts/test_mmSolver_linux_maya2024.bash tests/test/test_api/

# Manual execution:
$ /usr/autodesk/mayaVERSION/bin/mayapy tests/runTests.py
# We can test specific files like this:
$ /usr/autodesk/mayaVERSION/bin/mayapy tests/runTests.py tests/test/test_api/test_attribute.py
```

On Windows run:
```cmd
> CD <project root>

REM Using convenience test scripts:
> scripts\test_mmSolver_windows64_maya2024.bat
REM We can test specific files like this:
> scripts\test_mmSolver_windows64_maya2024.bat tests\test\test_api\test_attribute.py
REM Run all API tests:
> scripts\test_mmSolver_windows64_maya2024.bat tests\test\test_api\

REM Manual execution:
> "C:\Program Files\Autodesk\MayaVERSION\bin\mayapy" tests\runTests.py > tests.log
REM We can test specific files like this:
> "C:\Program Files\Autodesk\MayaVERSION\bin\mayapy" tests\runTests.py tests\test\test_api\test_attribute.py > tests.log
```

Make sure you use the same Maya version 'mayapy' for testing as you
have built ``mmSolver`` with.

On Windows, 'cmd.exe' is very slow printing text to the console,
therefore redirecting to a log file ('> file.log' below) will improve
performance of the test suite greatly.

For more information about testing, see the Testing section in
[DEVELOPER.md](https://github.com/david-cattermole/mayaMatchMoveSolver/blob/master/DEVELOPER.md).

# Run Test Suite inside Maya GUI

You may also wish to run the test suite inside the Maya GUI.
You can do this using the following snippet executed inside the 
Maya Script Editor.

```python
import sys
import os
dev_path = 'C:/Users/user/dev/mayaMatchMoveSolver/'
runTest_path = os.path.join(dev_path, 'tests')
if runTest_path not in sys.path:
    sys.path.append(runTest_path)

import runTests

# reload the module you are testing
import test.test_api.test_solve as mod
reload(mod)

path_list = []
# # Uncomment to run tests from test_solve.py only.
# path_list.append(os.path.join(dev_path, 'tests/test/test_api/test_solve.py'))
runTests.main(path_list)
```

# Caveats

Some Maya versions work with the test suite and others fail to 
run in the 'mayapy' executable. For an unknown reason Maya 2018 fails
to run tests with the 'mayapy' executable. This problem is being 
investigated, any hints, solutions or Pull Requests are appreciated to
improve and fix the build system for mmSolver.
