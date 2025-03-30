# Profiles

When each test is run it also starts a Python profiler (using
`cProfile`). The output of these profiles are saved in the
`./tests/profile` directory. For solver tests, there is also output
from Maya's internal DG Profiler, you may visualise this data using the
[Maya Profiler window](https://knowledge.autodesk.com/support/maya/learn-explore/caas/CloudHelp/cloudhelp/2016/ENU/Maya/files/GUID-3423BE20-0F03-422D-A05A-A1757C7B0A70-htm.html)
inside Maya.

## Visualizing Profile Data

### Using Python

To visualise the Python profile data, try running the following Python code:
```python
import pstats
path = '/path/to/file.pstat'
s = pstats.Stats(path)
s = s.sort_stats('cumulative')
s.print_stats()
```

### Using Provided Scripts

#### On Windows

To generate visualizations from your profile data, open a Command
Prompt (cmd.exe), navigate to the project directory and run:

```commandline
> cd c:/path/to/mayaMatchMoveSolver
> call scripts/generate_profile_visualisation_windows64_maya2020.bat
```

This script will:
- Process all `.pstat` files in the `./tests/profile/` directory.
- Generate FlameGraph SVG visualisations for each profile.
- Create human-readable text summaries of the profiles.

You can find the generated files in the same directory as the original
`.pstat` files.

#### On Linux

Similar functionality is available on Linux using the bash script
equivalents:

```bash
$ cd /path/to/mayaMatchMoveSolver
$ bash scripts/generate_profile_visualisation_linux_maya2020.bash
```

### FlameGraph SVG

Please note the FlameGraph generation requires the
[inferno](https://github.com/jonhoo/inferno) tool to be installed.

You can easily install inferno via Rust's Cargo package manager:
```commandline
> cargo install inferno
```

Once the SVG visualisations files are created you can open the .svg
files in a web-browser to interactively browse the contents.
