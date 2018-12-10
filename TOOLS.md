# Tools

Most users will use the tools listed below to control and manipulate
the MM Solver. There are also utilities to help the MM Solver
workflow.

## Solver UI
This UI is designed to allow all aspects of the mmSolver command.

To open the Solver run this Python command:
```python
import mmSolver.tools.solver.tool as solver
solver.open_window()
```

![Solver UI](https://raw.githubusercontent.com/david-cattermole/mayaMatchMoveSolver/master/design/ui/mmSolver.png)

### Objects

This section of the UI displays the marker objects that will be used
for solving.

### Attributes

This section of the UI shows the Attributes that will be used for
solving.

### Solver Steps

You can add multiple solver "steps", each step is performed going
**downwards**, first #1, then #2, #3, etc.

When you hit the "solve" button you are performing all of the solve steps.

the 'Override Current Frame' check-box allows the user to temporarily override the time for all Solve Steps with the current frame. The current frame value dynamically updates as the user changes the Maya frame. The original solver frame numbers are always stored and never overwritten.

Each Solver "step" contains:

- Enabled
- Frames
- Attributes
- Strategy

#### Enabled

Should we use the solver step or not?

This is a text input (currently), type "yes", or "no", "y" or "n", or
"true" or "false" (and other common english words), to set the state.

#### Frames

This is the list of frames to solve.

The frame numbers can be entered as "#-#" to define a range, or
"#,#,#,#" to define a list of individual frame numbers.

Examples are "1,10,20,30,40,50" or "10-20,30,40-50".

Once text is entered the UI will evaluate the list and re-create the
string shown.

#### Attributes

This is a filter of the attributes used in the solve step.

You may type into this field either one of these options:

- "Animated Only" - Use only the animated attributes
- "Static + Animated" - Use the static and animated attributes

#### Strategy

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

## Create Marker

Create a default Marker node.

Run this Python command:
```python
import mmSolver.tools.createmarker.tool as createmarker_tool
createmarker_tool.create_marker()
```

## Convert to Marker

Converts the selected transform nodes into screen-space Markers, as viewed though the active viewport camera.

The created markers are named based on the selected transform nodes, and are parented under the active viewport camera.

Run this Python command:
```python
import mmSolver.tools.createmarker.tool as createmarker_tool
createmarker_tool.create_marker()
```

## Load Markers

The Load Markers UI allows loading of .txt, .uv and .rz2 files.

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

For .txt, unfortunately the resolution is not yet given, and so you'll
need to scale the animation curves manually. The "Option" value is
intended to become the resolution Width / Height for the .txt format,
but is not yet connected up.

Run this Python command:
```python
import mmSolver.tools.loadmarker.ui.loadmarker_window as loadmarker_window
loadmarker_window.main()
```

## Create Bundle

Create a default Bundle node.

If Markers are selected, the Bundle will attempt to attach to it, while adhering to the rule; *a bundle can only have one marker representation for each camera.*

Run this Python command:
```python
import mmSolver.tools.createbundle.tool as createbundle_tool
createbundle_tool.create_bundle()
```

## Link Marker + Bundle

Link the selected Marker and Bundle together.

The link will not succeed if the selected Bundle is already connected to a Marker with the same camera, or in other words; A bundle can only have one Marker per-camera. This tool checks and adheres to this requirement.

Run this Python command:
```python
import mmSolver.tools.linkmarkerbundle.tool as link_mb_tool
link_mb_tool.link_marker_bundle()
```

## Unlink Marker from all Bundles

Unlink all the Bundles from all selected Markers.

Run this Python command:
```python
import mmSolver.tools.linkmarkerbundle.tool as link_mb_tool
link_mb_tool.unlink_marker_bundle()
```

## Toggle Marker / Bundle

Select the opposite node, if a Marker is selected, select it's connected Bundle, and vice versa.

Run this Python command:
```python
import mmSolver.tools.selection.tool as selection_tool
selection_tool.swap_between_selected_markers_and_bundles()
```

## Select Marker + Bundle

With either a Marker or Bundle selected, select both connected nodes.

Run this Python command:
```python
import mmSolver.tools.selection.tool as selection_tool
selection_tool.select_both_markers_and_bundles()
```

## Center 2D On Selection

Forces the active viewport camera to lock it's center to the currently selected transform node.

A viewport camera can only center on one node at a time.

Run this Python command:
```python
import mmSolver.tools.centertwodee.tool as centertwodee_tool
centertwodee_tool.center_two_dee()
```

## Aim at Camera

Aim the selected transform nodes toward the active viewport camera.

Run this Python command:
```python
import mmSolver.tools.cameraaim.tool as cameraaim_tool
cameraaim_tool.aim_at_camera()
```


