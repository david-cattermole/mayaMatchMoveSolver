# Developing Maya MatchMove Solver

So, you'd like to contribute to the Maya Matchmove Solver? That's great! 

Below is a list of the conventions used on the project.

# Python

This project uses [PEP 8 coding style](https://www.python.org/dev/peps/pep-0008/).

Here is a specific list, some are listed in PEP 8, some are not: 
- Line limit of 80 characters, exceptions are allowed if required.
- Use 4 spaces for indentation, do not use tabs.
- Each top-level function definition should have 2 blank line of space between it, 1 blank line separates class functions/methods.
- All modules should should have a doc-string, with a brief description in a single at minimum.
- Functions should have a doc-string.
- Doc-strings should use triple double-quote characters: `"""My doc-string"""`
- Private variables are specified by `_`; `_variable`. These variables should not be called directly, getters and setters should be written.
- Constant variables should be specified at the top of a module and must be `UPPER_CASE`.
- Do not use `global` variables, unless you really, really need to.
- Remove all redundant white space in source code.

# C++

- The coding style is K+R.
- Line limit of 120 characters maximum, but keeping code below 80 characters is advised.
- Function names use lower camel case: `myFunctionName`.
- Class names use upper camel case: `MyClassName`.
- Class variables use a `m_` prefix, and use lower camel case name: `m_myVariable`.
- Static class variables use a `s_` prefix, and use lower camel case name: `m_myVariable`.
- All class variables should be private, and provide getters / setters for accessing class variables.
- All defines are `UPPER_CASE_WITH_UNDERSCORES`.
- Remove all redundant white space in source code.