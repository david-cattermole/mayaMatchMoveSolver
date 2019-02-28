.. _load-markers-ref:

Load Markers
============

The Load Markers UI allows loading of ``.uv`` (mmSolver), ``.txt``
(3DEqualizer4), ``.rz2`` (Autodesk MatchMover) formated files.

When opening the UI, the contents of the user’s clipboard is
queried. If the clipboard is a valid file path, it will be
automatically pasted into the “File Path”, so you won’t need to
“Browse” for the file.

In 3DEqualizer, the "Copy 2D Tracks (MM Solver)" is designed to copy
the selected 2D points to a temporary file path and then place that
file path on the clipboard automatically. Once the file path is on the
clipboard, just open the Maya Load Marker tool and the path will be
read automatically.

The "Camera" list contains all the cameras currently in the Maya
scene. If no cameras are available (persp, front, top, left do not
count), the default option is to create a new camera. The "Update"
button refreshes the "Camera" list without needing to close and
re-open the UI.

Once a file path is given, press the “Load” button.
For ``.txt`` format you will need to enter the Width / Height of the input
format.


.. figure:: images/tools_loadmarker_overview.png
    :alt: Load Markers UI
    :align: center
    :width: 66%

    Load Markers UI

Python Function
---------------

Run this Python command:

.. code:: python

    import mmSolver.tools.loadmarker.ui.loadmarker_window as loadmarker_window
    loadmarker_window.main()

