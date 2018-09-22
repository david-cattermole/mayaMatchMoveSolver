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

# Testing

Testing is an essential step in the Maya Matchmove Solver project, all
new code written should have a unit and/or integration test. It is our
aim to have confidence that the tool is running correctly when all
tests are run without error.

## Running Tests

Running all the entire test suite is simple:

```commandline
$ cd <project root>
$ sh runTests.sh
```

You may also test a specific test or list of tests using:

```commandline
$ cd <project root>
$ sh runTests.sh ./tests/test/name/of/test/file.py
```

Multiple test files can be given to the ``runTests.sh`` script. You
may also run multiple tests by giving a directory, this will run all
tests in the directory.

Before pushing code, *always* run all tests and fix any errors that
occur. After a code push, none of the tests should fail.

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
