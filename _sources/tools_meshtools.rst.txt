Mesh Tools
==========

Mesh tools will create, modify or operate on meshes. These tools are
intended to augment Autodesk Maya's existing modeling tool-set and be
specific to the common use cases for MatchMove tasks.

.. _mesh-from-points-ref:

Mesh From Points
----------------

The `Mesh From Points` tool is used to generate a triangulated mesh
from a set of 3D points. The generated mesh is extremely helpful to
create a 3D visualisation, or as a starting point for a refined
hand-generated model.

`Mesh From Points` uses a type of `Delaunay Triangulation
<https://en.wikipedia.org/wiki/Delaunay_triangulation>`_ named
`Delaunator <https://github.com/mapbox/delaunator>`_, which is
optimised to generate meshes for landscape meshes. As a result, the
camera viewing position of the points is used to triangulate the
points in camera-space.

.. figure:: images/tools_mesh_from_points_window.png
    :alt: Mesh from Points Window.
    :align: right
    :width: 100%

.. note:: September, 2024; The Mesh From Points tools cannot be undone.
          This is intended to be fixed in a future release.

Usage:

1) Select a transform nodes.

   - At least 3 transform nodes are required.

2) Activate a Maya viewport, and adjust the camera view to see the
   points.

   - If your points represent a landscape, adjust the camera to view
     all nodes from the "sky" point of view (from Y+, looking
     downwards).

3) Run `Create Full Mesh From Points` tool.

   - Optionally, use the `Create Border Mesh From Points` or open the
     `Mesh From Points` UI.

   - The `Create Border Edge Strip Mesh` button in the `Mesh From
     Points` can be used create a mesh with extra geometry at the
     edges. This is intended to be used to create a "patch" of
     geometry that can be adjusted further using Maya's modelling
     tools. Adjust the `Border Edge Strip Width` slider to adjust the
     position of the edges.

To create a mesh from the selected nodes, use this Python command:

.. code:: python

    import mmSolver.tools.meshfrompoints.tool as tool
    tool.create_full_mesh()

    # Or create the border mesh only.
    tool.create_border_mesh()

To open the window, use this Python command:

.. code:: python

    import mmSolver.tools.meshfrompoints.tool as tool
    tool.main()
