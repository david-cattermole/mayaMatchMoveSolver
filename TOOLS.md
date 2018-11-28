# Tools

Most users will use the tools listed below to control and manipulate
the MM Solver. There are also utilities to help the MM Solver
workflow.

## Solver
This UI is designed to allow all aspects of the mmSolver command

You can add multiple solver "steps", each step is performed going
downwards, first #0, then #1, #2, etc.

When you hit the "solve" button you are performing all of the solve steps..

Each Solver "step" contains:

- Enabled
- Attributes
- Frames
- Strategy

![Solver UI](https://raw.githubusercontent.com/david-cattermole/mayaMatchMoveSolver/master/design/ui/mmSolver.png)

### Enabled

Should we use the solver step or not?

This is a text input (currently), type "yes", or "no", "y" or "n", or
"true" or "false" (and other common english words), to set the state.

### Attributes

This is a filter of the attributes, should the solver step solve only
Animated attributes, only Static attributes or both Static and
Animated attributes.

You may type into this field either one of these options:

- "Animated Only"
- "Static Only" (currently not implemented)
- "Static + Animated"
- "No Attributes" - Same as disabling the solver step.

### Frames

This is the list of frames to solve.

The frame numbers can be entered as "#-#" to define a range, or
"#,#,#,#" to define a list of individual frame numbers.

Examples are "1,10,20,30,40,50" or "10-20,30,40-50".

Once text is entered the UI will evaluate the list and re-create the
string shown.

### Strategy

This is the "solving strategy"; how the frames and attributes are
ordered in the solving process.

There are two currently supported strategies:

- "Two Frames Fwd" - Each pair of sequential frames are solved
  together; frame 1 and 2, then 2 and 3, then 3 and 4, etc.

- "All Frames" - All numbers are solved together, at once (also
   called a "global solve").

If the "Animated Only" attribute filter is currently used, then the
strategies above are unused and instead we loop over the frames
sequentially and solve each frame independent of any other frame.
This is the fastest method, but cannot solve Static attributes.


## Load Markers

The Load Markers UI allows loading of .txt, .uv and .rz2 files.

For .txt, unfortunately the resolution is not yet given, and so you'll
need to scale the animation curves manually. The "Option" value is
intended to become the resolution Width / Height for the .txt format,
but is not yet connected up.

When opening the UI, the contents of the user's clipboard is queried
and if it looks like a file path, it will be automatically pasted into
the "File Path", so you won't need to "Browse" for the file. In
3DEqualizer, I have a script designed to copy the selected 2D points
to a temporary file path and then place that file path on the
clipboard automatically. This would be my recommended workflow with
3DEqualizer.

The "Camera" list contains all the cameras currently in the Maya
scene. If no cameras are available (persp, front, top, left do not
count), the default option is to "<Create New Camera>". The "Update"
button refreshes the "Camera" list without needing to close and
re-open the UI.

Once a file path is given, press the "Load" button.

![Load Markers UI](https://raw.githubusercontent.com/david-cattermole/mayaMatchMoveSolver/master/design/ui/loadMarkers.png)
