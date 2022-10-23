Other Commands
==============

*To be written.*

``mmReprojection`` Command
++++++++++++++++++++++++++++++

*To be written.*

``mmTestCameraMatrix`` Command
++++++++++++++++++++++++++++++

`mmTestCameraMatrix` calculates an matrix (not returned) from the
given camera transform and shape nodes. If the matrix matches the same
matrix produced by Maya's API, then the command returns true.

This command is used for internal tests only, it has no practical use
for users.

Python Example:

.. code:: python

   cam_tfm = maya.cmds.createNode('transform', name='cam_tfm')
   cam_shp = maya.cmds.createNode('camera', name='cam_shp', parent=cam_tfm)
   result = maya.cmds.mmTestCameraMatrix(cam_tfm, cam_shp)
   assert result == True
