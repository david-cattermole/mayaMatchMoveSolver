Display Commands
================

Display commands control mmSolver's custom Viewport 2.0 renderers.
Two renderers are provided — MM Standard Renderer and MM Silhouette
Renderer — each registered as a Viewport 2.0 override and documented
in detail in :ref:`Viewport Renderers <renderer-ref>`.

Each renderer exposes a thin Maya command that forces a refresh of the
active 3D view. Settings for the Silhouette Renderer are stored on the
``mmRenderGlobalsSilhouette`` node and adjusted via ``setAttr``.


``mmRendererStandard`` Command
++++++++++++++++++++++++++++++

``mmRendererStandard`` triggers a forced refresh of the active Viewport
2.0 panel when the MM Standard Renderer is active. It supports
``-query`` mode (no flags beyond enabling query are defined). The
command is not undoable.

See :ref:`renderer-ref` for how to activate and use the MM Standard
Renderer.

Flags
-----

The command accepts ``-query`` mode only. No additional flags are
defined; calling the command refreshes the active view.

Return
------

Returns nothing.

Example
-------

Python Example:

.. code:: python

   import maya.cmds

   # Force a refresh of the active view.
   maya.cmds.mmRendererStandard()

MEL Example:

.. code:: text

   mmRendererStandard;


``mmRendererSilhouette`` Command
+++++++++++++++++++++++++++++++++

``mmRendererSilhouette`` triggers a forced refresh of the active
Viewport 2.0 panel when the MM Silhouette Renderer is active. It
supports ``-query`` mode (no flags beyond enabling query are defined).
The command is not undoable.

The silhouette effect is configured through the
``mmRenderGlobalsSilhouette`` node, which is created automatically when
the renderer is first activated. Use ``setAttr`` to change the
settings described below.

See :ref:`renderer-silhouette-ref` for full usage instructions and a
description of each setting.

Flags
-----

The command accepts ``-query`` mode only. No additional flags are
defined; calling the command refreshes the active view.

``mmRenderGlobalsSilhouette`` Node Attributes
---------------------------------------------

The silhouette settings live on the ``mmRenderGlobalsSilhouette`` node.

======================== ========= =============== =========================================================
Attribute                Type      Default         Description
======================== ========= =============== =========================================================
``enable``               bool      ``true``        Toggle the silhouette effect on or off.
``overrideColor``        bool      ``true``        Use the ``color`` attribute for all objects.
``depthOffset``          float     ``-1.0``        Depth separation between solid and wireframe geometry.
``width``                float     ``2.0``         Width of silhouette lines.
``color``                float3    ``0, 1, 0``     Silhouette line colour (green by default).
``alpha``                float     ``1.0``         Opacity of silhouette lines.
``cullFace``             enum      ``Back``        Back-face culling; ``Back``, ``Front``, ``FrontAndBack``.
``operationNum``         uint8     ``255`` (all)   Limit rendering to the first N operations (debug).
======================== ========= =============== =========================================================

Return
------

Returns nothing.

Example
-------

Python Example:

.. code:: python

   import maya.cmds

   # Force a refresh of the active view.
   maya.cmds.mmRendererSilhouette()

   # Change the silhouette colour to red.
   maya.cmds.setAttr('mmRenderGlobalsSilhouette.color', 1, 0, 0, type='double3')

   # Increase line width.
   maya.cmds.setAttr('mmRenderGlobalsSilhouette.width', 3.0)

   # Disable the effect temporarily.
   maya.cmds.setAttr('mmRenderGlobalsSilhouette.enable', False)

MEL Example:

.. code:: text

   mmRendererSilhouette;

   // Change silhouette colour to red.
   setAttr mmRenderGlobalsSilhouette.color -type double3 1 0 0;

   // Increase line width.
   setAttr mmRenderGlobalsSilhouette.width 3.0;

   // Disable the effect temporarily.
   setAttr mmRenderGlobalsSilhouette.enable false;
