# Profiles

When each test is run it also starts a Python profiler (using
`cProfile`). The output of these profiles are saved in the
`./tests/profile` directory. For solver tests, there is also output
from Maya's internal DG Profiler, you may visualise this data using the
[Maya Profiler window](https://knowledge.autodesk.com/support/maya/learn-explore/caas/CloudHelp/cloudhelp/2016/ENU/Maya/files/GUID-3423BE20-0F03-422D-A05A-A1757C7B0A70-htm.html)
inside Maya.

To visualise the Python profile data, try running the following Python code:
```python
import pstats
path = '/path/to/file.pstat'
s = pstats.Stats(path)
s = s.sort_stats('cumulative')
s.print_stats()
```
