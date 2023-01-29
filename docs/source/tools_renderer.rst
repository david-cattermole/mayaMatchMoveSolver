.. _renderer-ref:

MM Renderer
===========

`MM Renderer` is a Viewport 2.0 renderer designed to add helpful
features for use with MatchMove workflows and reviews.

This tool is currently only in beta, and is not enabled in stable `MM
Solver` releases.

.. figure:: images/tools_renderer_menu.png
    :alt: Viewport Renderer menu
    :align: center
    :scale: 80%

    Enable `MM Renderer` in the "Renderer" menu on each Viewport.

`MM Renderer` is different from regular Viewport 2.0 because it has
the following features:

- 2D Composite objects in "layers" to force objects in front/behind
  others.
- Show a edges for objects.
- Supports "Hidden Line" rendering, without needing to enable "Hold
  Out" toggles or assign a useBackground shader.

Getting Started
~~~~~~~~~~~~~~~

1) Load mmSolver plug-in.

   To use `MM Renderer`, simply load the mmSolver plug-in (for example
   open the Solver UI to ensure the plug-in is loaded), then use the
   Viewport's "Renderer" menu to switch to "MM Renderer (beta)".

2) Add objects into Display Layers.

   Initially you'll likely find all objects are invisible(!), however
   that's just a small-ish bug, and you'll simply need to add your
   objects to a Maya Display Layer to see them.

3) Adjust Display Layer attributes.

   Once your objects are in a Display Layer you can use the Display
   Layer's "Extra Attributes" in the Attribute Editor to control specific
   options for how the objects in each layer are displayed.

Display Layers
~~~~~~~~~~~~~~

.. figure:: images/tools_renderer_display_layers.png
    :alt: MM Renderer Display Layers
    :align: right
    :scale: 60%

Display Layers can be used to add custom attributes (recognized only
by `MM Renderer`) that can customize the display of the objects.

Using these attributes you can:

- Control how different Display Layers are combined (merged)
  together - like in a layer-based composting software (eg Photoshop).
- For a specific display mode (Shaded, Wireframe, Hidden Line, etc)
- Toggle display of object edges.
- Control the alpha of different effects (Layer Mix mode, Objects and Edges)

Python Function
~~~~~~~~~~~~~~~

The commands below are available for this tool, and allow hotkeys or
custom buttons to be created.

Add `MM Renderer` custom attributes to selected displayLayer nodes:

.. code:: python

    import mmSolver.tools.mmrendererlayers.tool as tool
    tool.main()

Add `MM Renderer` custom attributes to all displayLayer nodes in the current Maya scene:

.. code:: python

    import mmSolver.tools.mmrendererlayers.tool as tool
    setup_all_layers.main()
