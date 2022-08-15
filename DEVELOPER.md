# Developing Maya MatchMove Solver

So, you'd like to contribute to the Maya Matchmove Solver? That's
great!

# Project Conventions

Below is a list of the conventions used on the project.

## Python Code Style

This project uses [PEP 8
codingstyle](https://www.python.org/dev/peps/pep-0008/), and uses the
[Black](https://pypi.org/project/black/) formatting tool to enforce
the format.

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

## C++ Code Style

The coding style is based on the Google coding style, and is
configured in the `.clang-format` file in the root
directory. [Clang-format](https://clang.llvm.org/docs/ClangFormat.html)
is used to automatically format C++ files.

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

# Best Practices

These guidelines should be followed whenever adding, changing or
modifying code to the project, however these are only guidelines, not
rules. Use your judgement and if the guidelines don't fit, don't use
them.

## General


- General
  - Don't repeat yourself (DRY)
    - Identify repeated code and split the code into smaller re-usable
      pieces.
    - Reuse code, don’t duplicate it.
  - Fail fast
    - Return an error or raise an exception as early as possible.
    - Use `assert` calls to ensure expected types are given to functions.
  - Use names to explain to other people.
    - [CppCon 2019: Kate Gregory "Naming is Hard: Let's Do Better"](https://www.youtube.com/watch?v=MBRoCdtZOYg)
  - Write the simpliest code possible - do not try to write overly
    complex or "clever" code unless required.
  - Use comments to explain *why* the code exists, not *what* the code
    does.
  - Add documentation for arguments and return types, and describe what
    is not obvious.
  - Avoid hard-coded values (numbers and strings), use named constants
    with values.
- Functions
  - Functions should do *one* thing, and one thing *only*.
  - Functions should be *shorter* rather than *longer*.
  - Ideally all functions should be
    [pure](https://en.wikipedia.org/wiki/Pure_function), or as pure as
    practical. This means:
    - If the same arguments are given, the exact same result should be
      returned.
    - The function should not use global variables or change any
      shared state.
- Classes
  - Do not use classes unless nessarary.
  - Avoid class inheritance, and instead use 'composition' of objects
    and classes.
  - When class inheritance is needed, use an Abstract Base Class (ABC)
    interface and sub-class from it.
- Tests
  - Write tests for new features.
  - Make sure tests pass before and after modifications.
- Exceptions
  - Exceptions should be for exceptional cases, not to avoid type or
    value checking.

## Python

Best practices specific to Python.

- The [Zen Of Python](https://peps.python.org/pep-0020/) is wise and
  you should follow it.

## C++

To be written.

# Building Individual Components

To speed up compilation you may turn off individual components of the
CMake build. For example, the BUILD_PLUGIN and BUILD_DOCS is slower to
build than just BUILD_PYTHON.

You may control this with the Build options below, which are defined
(all ON) in the provided `./scripts/build_mmSolver_*` scripts.

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

# Setup Linux Build Environment With Docker

If you are developing on Windows and need to test for Linux, or if you
are using Linux but you don't want to modify your computer's system
environment, or you are running an incompatible, newer or older Linux
distribution, it is highly recommended you use
[Docker](https://www.docker.com/) to help install and configure the
exact dependencies needed for building. These Dockerfiles are used for
the final releases of mayaMatchMoveSolver - so they are perfectly
compatible and will work on any supported Linux Maya installation.

Note: Although Docker can be used for building and testing, Docker
does not allow the Maya UI to be run. Therefore you must test on a
Linux installation with the `mayaMatchMoveSolver` files that are
built.

The mayaMatchMoveSolver project comes with pre-configured Dockerfiles
in the project root, named as `Dockerfile_mayaXXXX` for each supported
Maya version.

To get started with development on Windows, first install [Docker
Desktop](https://www.docker.com/products/docker-desktop/) which
includes the core `docker` command and a GUI. Once Docker Desktop is
installed your computer will need to be restarted, before it's fully
working.

To set up the Docker environment with a Maya installation available
and ready for building/testing you must download the Maya Linux
installation file from the [Autodesk Maya
website](https://www.autodesk.com/products/maya/overview), and place
it into the `<project root>/external/archives/` directory. The Maya
installation file should look like
`Autodesk_Maya_2022_ML_Linux_64bit.tgz`, or a similar naming
convention. The `Dockerfile_mayaXXXX` file will install Maya using
this file - if the file name is slightly different you can change the
Dockerfile.

Next, open a Windows Powershell, navigate to the `mayaMatchMoveSolver`
project root and run the docker container in PowerShell:

```
PS > cd <project root>
PS > docker build --file Dockerfile_mayaXXXX -t mmsolver-linux-mayaXXXX-build .
PS > docker run --rm --interactive --volume "${pwd}:/mmSolver" --tty mmsolver-linux-mayaXXXX-build
```

Note: Replace XXXX, with the Maya version to build for.

For further help open the `Dockerfile_mayaXXXX` files in a text editor
to see helpful information at the top of each file.

Once the `docker run` command is run, you will have a Linux (bash)
shell you can type commands into. To build mmSolver inside Docker
simply run the build commands as normal:

```
$ ./scripts/build_thirdparty_linux_maya2022.bash
$ ./scripts/build_mmSolver_linux_maya2022.bash
$ mayapy tests/runTests.py
```

# Python Tools

## Python Virtual Environment

Linux (using `bash`):
```
$ source ./scripts/python_venv_activate_maya2022.bash
$ # Run commands here...
$ deactivate
```

Windows (using `cmd.exe`):
```
> python_venv_activate_maya2022.bat
> REM Run commands here...
> python_venv_deactivate_maya2022.bat
```

## Python Code Formatting

```
$ ./scripts/python_formatter_run_black_check.bash
$ ./scripts/python_formatter_run_black_edit.bash
```

```
> scripts/python_formatter_run_black_check.bat
> scripts/python_formatter_run_black_edit.bat
```

## Python and C++ Linting

Linux (using `bash`):
```
$ ./scripts/python_linter_run_pylint.bash
$ ./scripts/python_linter_run_flake8.bash
$ ./scripts/python_linter_run_cpplint.bash
```

Windows (using `cmd.exe`):
```
> scripts/python_linter_run_cpplint.bat
> scripts/python_linter_run_flake8.bat
> scripts/python_linter_run_pylint.bat
```

## Upgrading Python 2 to 3

Linux (using `bash`):
```
$ ./scripts/python_convert_run_2to3.bash
```

Windows (using `cmd.exe`):
```
> scripts/python_convert_run_2to3.bat
```

# C++ Tools

For C++ code use
[clang-format](https://clang.llvm.org/docs/ClangFormat.html) (which is
part of the [LLVM](https://llvm.org/) Clang toolset) for automatic
code formatting.

To check for common issues you can use
[cpplint](https://pypi.org/project/cpplint/) or
[cppcheck](http://cppcheck.net/).

## C++ Code Formatting

The C++ code in mmSolver should be automatically formatted with
`clang-format` using the following scripts:
```
$ cd <project root>
$ ./scripts/cpp_formatter_run_clang_format_check.bash  # checks files match formatting rules.
$ ./scripts/cpp_formatter_run_clang_format_edit.bash   # edits the files
```

NOTE: On Windows, use the `.bat` scripts instead.

On Linux you can usually install the Clang via the package management
system (although the packages in CentOS 7 are far too old to be used).

On Windows you can install the LLVM/Clang toolset as part of Visual
Studio 2017 or 2019.

The configuration of the formatting is already defined in the
`.clang-format` file in the project root.

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

Currently [clang-tidy](https://clang.llvm.org/extra/clang-tidy/) is
not set up for mayaMatchMoveSolver (feel free to add
support/documentation and submit a PR).

C++ code linting is not (yet) enforced.

# Rust Tools

To format all Rust code please use `cargo fmt` that comes with Rust.

To check your Rust code for common issues use the `cargo clippy`
command.

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

Please read the
[tests/README.md](https://github.com/david-cattermole/mayaMatchMoveSolver/blob/master/tests/README.md)
file for more details on running the test suite.

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
