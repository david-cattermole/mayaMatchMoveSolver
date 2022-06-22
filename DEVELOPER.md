# Developing Maya MatchMove Solver

So, you'd like to contribute to the Maya Matchmove Solver? That's
great!

# Project Conventions

Below is a list of the conventions used on the project.

## Python

This project uses [PEP 8 codingstyle](https://www.python.org/dev/peps/pep-0008/).

Here is a specific list, some are listed in PEP 8, some are not: 
- Line limit of 80 characters, exceptions to this rule are allowed if
  required.
- Use 4 spaces for indentation, do not use tabs.
- Each top-level function definition should have 2 blank line of space
  between it, 1 blank line separates class functions/methods.
- All modules should should have a doc-string, with a brief
  description in a single at minimum.
- Functions should have a doc-string.
- Doc-strings should use triple double-quote characters: 
  `"""My doc-string"""`
- Private variables are specified by `_`; `_variable`. These variables
  should not be called directly, getters and setters should be
  written.
- Constant variables should be specified at the top of a module and
  must be `UPPER_CASE`.
- Do not use `global` variables, unless you really, really need to.
- Remove all redundant white space in source code.

## C++

- The coding style is K+R.
- Line limit of 120 characters maximum, but keeping code below 80
  characters is advised.
- Function names use lower camel case: `myFunctionName`.
- Class names use upper camel case: `MyClassName`.
- Class variables use a `m_` prefix, and use lower camel case name:
  `m_myVariable`.
- Static class variables use a `s_` prefix, and use lower camel case
  name: `m_myVariable`.
- All class variables should be private, and provide getters / setters
  for accessing class variables.
- All defines are `UPPER_CASE_WITH_UNDERSCORES`.
- Remove all redundant white space in source code.

# Building Individual Components

To speed up compilation you may turn off individual components of the 
CMake build. For example, the BUILD_PLUGIN and BUILD_DOCS is slower to 
build than just BUILD_PYTHON.

You may control this with the Build options below, which are defined 
(all ON) in the provided ```./scripts/build_mmSolver_*``` scripts. 

In the Bash Shell scripts:
```shell script
# Build options, to allow faster compilation times. (not to be used by
# users wanting to build this project.)
BUILD_PLUGIN=1
BUILD_PYTHON=1
BUILD_MEL=1
BUILD_QT_UI=1
BUILD_DOCS=1
BUILD_ICONS=1
BUILD_CONFIG=1
BUILD_TESTS=1
```

Or in Windows Batch files:
```cmd
:: Build options, to allow faster compilation times. (not to be used by
:: users wanting to build this project.)
SET BUILD_PLUGIN=1
SET BUILD_PYTHON=1
SET BUILD_MEL=1
SET BUILD_QT_UI=1
SET BUILD_DOCS=1
SET BUILD_ICONS=1
SET BUILD_CONFIG=1
SET BUILD_TESTS=1
```

# C++ Tools

## C++ Code Formatting

The C++ code in mmSolver should be automatically formatted using the
following scripts:
```
$ cd <project root>
$ ./scripts/cpp_formatter_run_clang_format_check.bash  # checks files match formatting rules.
$ ./scripts/cpp_formatter_run_clang_format_edit.bash   # edits the files
```

NOTE: On Windows, use the `.bat` scripts instead.

These scripts use `clang-format`, which is part of the
[LLVM](https://llvm.org/) Clang toolset.

On Linux you can usually install the Clang via the package management
system (although the packages in CentOS 7 are far too old to be used).

On Windows you can install the LLVM/Clang toolset as part of Visual
Studio 2017 or 2019.

## C++ Linting

To help spot common issues and keep the code clean you can use
cpplint, with the following script:

```
$ cd <project root>
$ ./scripts/python_linter_run_cpplint.bash
```

Alternatively you may use [cppcheck](https://cppcheck.net/). Simply
install and run the GUI or tool with the mayaMatchMoveSolver project
directory. The `mayaMatchMoveSolver.cppcheck` can be used with
`cppcheck` for all configuration settings.

C++ code linting is not (yet) enforced.

# Testing

Testing is an essential step in the Maya Matchmove Solver project, all
new code written should have a unit and/or integration test. It is our
aim to have confidence that the tool is running correctly when all
tests are run without error.

## Running Tests

Running all the entire test suite is simple:

```commandline
$ cd <project root>
$ mayapy tests/runTests.py tests/test
```

You may also test a specific test or list of tests using:

```commandline
$ cd <project root>
$ mayapy tests/runTests.py tests/test/name/of/test/file.py
```

Multiple test files can be given to the ``runTests.py`` script. You
may also run multiple tests by giving a directory, this will run all
tests in the directory.

Before pushing code, *always* run all tests and fix any errors that
occur. After a code push, none of the tests should fail.

Please read the [tests/README.md](https://github.com/david-cattermole/mayaMatchMoveSolver/blob/master/tests/README.md) file for more details on 
running the test suite.

## Writing Tests

Tests should be saved with the file convention
``./tests/test/test_<category>/test*.py``. This naming convention will
allow the testing framework to guess that the file contains a test.

There are different categories for each component of Maya MatchMove
Solver: ``api``, ``solver`` and ``tools``. Tests related to a category
must be added to the corresponding component category.

Each category has a testing utilities module, to remove boiler-plate
code as much as possible and include automatic functionality, such as
Maya profiling and running Maya's 'New Scene' command when setting up
a test function. The test utility modules are
``test.test_api.apiutils``, ``test.test_solver.solverutils`` and
``test.test_tools.toolsutils``. Each module contains a 'TestCase'
class that should be sub-classed in each test file (see example file
below).

Here is example boiler-plate code for a test file written for the
``solver`` category.

```python
"""
Title - What is this testing?
"""

import unittest

try:
    import maya.standalone
    maya.standalone.initialize()
except RuntimeError:
    pass
import maya.cmds

import test.test_solver.solverutils as solverUtils
import mmSolver.api as mmapi


class TestModuleOrClassNameHere(solverUtils.SolverTestCase):

    def test_function_name_here(self):
        """
        What exactly are you testing? Is there anything specific about
        this test that should be noted?
        """
        # Do test here.
        return


if __name__ == '__main__':
    prog = unittest.main()
```
