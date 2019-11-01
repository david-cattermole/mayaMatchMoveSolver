Marker Bundle Tools
===================

Link Marker + Bundle
--------------------

Link the selected Marker and Bundle together.

The link will not succeed if the selected Bundle is already connected to
a Marker with the same camera, or in other words; A bundle can only have
one Marker per-camera. This tool checks and adheres to this requirement.

Run this Python command:

.. code:: python

    import mmSolver.tools.linkmarkerbundle.tool as tool
    tool.link_marker_bundle()

Unlink Marker from all Bundles
------------------------------

Unlink all the Bundles from all selected Markers.

Run this Python command:

.. code:: python

    import mmSolver.tools.linkmarkerbundle.tool as tool
    tool.unlink_marker_bundle()
