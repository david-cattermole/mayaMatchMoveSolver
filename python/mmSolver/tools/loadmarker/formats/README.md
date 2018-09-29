# Adding New Formats

To add a new file formats you must do the following steps:

1. Create a module under ``mmSolver.tools.loadmarker.formats```
2. Module must create a class inheriting from 'interface.LoaderBase', extending the 'parse' method. 
3. Add override static variables on the class for the new format.
4. Add an import to the ``mmSolver.tools.loadmarker.formats.__init__`` module. 
5. Add a test data file to ``./tests/data/<format name>/``.
6. Add a test function to read the test data file: ``./tests/test/test_tools/test_loadmarker.py``.
