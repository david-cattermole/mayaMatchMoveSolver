Image Commands
==============

Commands for reading and converting image files. These are used
internally by the image-plane and image-cache toolset, but can also be
called directly from Python or MEL scripts.

``mmReadImage`` Command
++++++++++++++++++++++++

``mmReadImage`` queries metadata from an image file without loading the
full pixel data into the scene. It runs in query mode only and is not
undoable.

Flags
-----

==================== ==================== ======= ============================================================== =============
Command Flag         Command Flag (short) Type    Description                                                    Default Value
==================== ==================== ======= ============================================================== =============
-widthHeight         -wh                  (none)  Return the image width and height in pixels.                   —
-dataHeader          -dhr                 (none)  Return extended header data (width, height, channels, bpc,     —
                                                  and total byte size).
-resolveFilePath     -rfp                 (none)  Return the resolved absolute file path, or ``None`` if the     —
                                                  file does not exist.
==================== ==================== ======= ============================================================== =============

The image file path is passed as a command object (the selection
string), not as a flag. Exactly one query flag must be set per call.

Return
------

- ``-widthHeight``: returns a list of two integers ``[width, height]``.
- ``-dataHeader``: returns a list of five strings
  ``[width, height, channel_count, bytes_per_channel, total_bytes]``.
- ``-resolveFilePath``: returns the resolved file path string, or
  ``None`` if the file cannot be found.

Example
-------

Python Example:

.. code:: python

   import maya.cmds

   file_path = '/path/to/image.exr'

   # Query width and height.
   wh = maya.cmds.mmReadImage(file_path, query=True, widthHeight=True)
   # e.g. [1920, 1080]

   # Query the full data header.
   header = maya.cmds.mmReadImage(file_path, query=True, dataHeader=True)
   # e.g. ['1920', '1080', '4', '4', '33177600']
   # Index 0 = width, 1 = height, 2 = channel count,
   # 3 = bytes per channel, 4 = total size in bytes.

   # Resolve the file path.
   resolved = maya.cmds.mmReadImage(file_path, query=True, resolveFilePath=True)

MEL Example:

.. code:: text

   string $file_path = "/path/to/image.exr";

   // Get width and height.
   int $wh[] = `mmReadImage -query -widthHeight $file_path`;

   // Get full data header.
   string $header[] = `mmReadImage -query -dataHeader $file_path`;

   // Resolve the file path.
   string $resolved = `mmReadImage -query -resolveFilePath $file_path`;


``mmConvertImage`` Command
+++++++++++++++++++++++++++

``mmConvertImage`` converts an image sequence from one file format to
another, optionally rescaling it in the process. This is primarily used
to bake image sequences to Maya IFF format for faster playback.

Frame numbers in the source and destination paths are represented by
``#`` characters (e.g. ``image.####.exr``); the padding width is
controlled separately by the ``-sourceFramePadding`` and
``-destinationFramePadding`` flags.

The command is not undoable.

Flags
-----

================================ ========================== ======== ======================================================================== =============
Command Flag                     Command Flag (short)       Type     Description                                                              Default Value
================================ ========================== ======== ======================================================================== =============
-source                          -src                       string   Source image sequence file path (use ``#`` for frame padding).           None
-destination                     -dst                       string   Destination image sequence file path.                                    None
-sourceFrameStart                -sfs                       unsigned First frame of the source sequence to convert.                           1
-sourceFrameEnd                  -sfe                       unsigned Last frame of the source sequence to convert.                            1
-sourceFramePadding              -sfp                       unsigned Frame number padding width for the source path.                          1
-destinationOutputFormat         -dof                       string   Output image format (e.g. ``"iff"``, ``"png"``, ``"exr"``).              ``"iff"``
-destinationFrameStart           -dfs                       unsigned First frame number to use in the destination sequence.                   1
-destinationFramePadding         -dfp                       unsigned Frame number padding width for the destination path.                     1
-resizeScale                     -rzs                       double   Uniform scale factor applied to the image resolution (e.g. 0.5 = half). 1.0
================================ ========================== ======== ======================================================================== =============

Return
------

Returns nothing. Converted files are written to disk.

Example
-------

Python Example:

.. code:: python

   import maya.cmds

   maya.cmds.mmConvertImage(
       source='sourceimages/stA/stA.#.jpg',
       destination='sourceimages/stA_CONVERT.#.iff',
       sourceFrameStart=0,
       sourceFrameEnd=94,
       sourceFramePadding=4,
       destinationOutputFormat='iff',
       destinationFrameStart=0,
       destinationFramePadding=4,
       resizeScale=0.5,
   )

MEL Example:

.. code:: text

   mmConvertImage
       -source "sourceimages/stA/stA.#.jpg"
       -destination "sourceimages/stA_CONVERT.#.iff"
       -sourceFrameStart 0
       -sourceFrameEnd 94
       -sourceFramePadding 4
       -destinationOutputFormat "iff"
       -destinationFrameStart 0
       -destinationFramePadding 4
       -resizeScale 0.5;


``mmImageCache`` Command
++++++++++++++++++++++++

``mmImageCache`` queries and manages the mmSolver in-process image
cache. It supports ``-query`` mode (to read cache state) and ``-edit``
mode (to change capacity or evict items). Capacity edits are undoable;
erase operations are not.

The cache is split into a **CPU** tier (RAM) and a **GPU** tier
(VRAM/textures). Each tier organises items into named groups — normally
one group per image sequence.

Flags
-----

Query-mode flags (use with ``-query``):

================================ ======================== ========== ======================================================= =============
Command Flag                     Command Flag (short)     Type       Description                                             Default Value
================================ ======================== ========== ======================================================= =============
-gpuCapacity                     -gpc                     (none)     GPU cache capacity in bytes.                            —
-cpuCapacity                     -cpc                     (none)     CPU cache capacity in bytes.                            —
-gpuUsed                         -gpu                     (none)     GPU memory currently used by the cache, in bytes.       —
-cpuUsed                         -cpu                     (none)     CPU memory currently used by the cache, in bytes.       —
-gpuItemCount                    -gic                     (none)     Total number of items in the GPU cache.                 —
-cpuItemCount                    -cic                     (none)     Total number of items in the CPU cache.                 —
-gpuGroupCount                   -ggc                     (none)     Number of groups in the GPU cache.                      —
-cpuGroupCount                   -cgc                     (none)     Number of groups in the CPU cache.                      —
-gpuGroupNames                   -ggn                     (none)     Names of all GPU cache groups.                          —
-cpuGroupNames                   -cgn                     (none)     Names of all CPU cache groups.                          —
-gpuGroupItemCount               -ggt                     (none)     Item count for the named GPU group (pass group name).   —
-cpuGroupItemCount               -cgt                     (none)     Item count for the named CPU group (pass group name).   —
-gpuGroupItemNames               -gin                     (none)     Item names for the named GPU group (pass group name).   —
-cpuGroupItemNames               -cin                     (none)     Item names for the named CPU group (pass group name).   —
-briefText                       -btx                     (none)     Return a human-readable cache summary string.           —
================================ ======================== ========== ======================================================= =============

For ``-gpuGroupItemCount``, ``-cpuGroupItemCount``, ``-gpuGroupItemNames``,
and ``-cpuGroupItemNames``, pass the group name as a command object
(the selection string).

Edit-mode flags (use with ``-edit``):

================================ ======================== ========== ============================================================= =============
Command Flag                     Command Flag (short)     Type       Description                                                   Default Value
================================ ======================== ========== ============================================================= =============
-gpuCapacity                     -gpc                     string     Set the GPU cache capacity to the given number of bytes.       —
-cpuCapacity                     -cpc                     string     Set the CPU cache capacity to the given number of bytes.       —
-gpuEraseItems                   -gei                     (none)     Evict named items from the GPU cache (not undoable).           —
-cpuEraseItems                   -cei                     (none)     Evict named items from the CPU cache (not undoable).           —
-gpuEraseGroupItems              -geg                     (none)     Evict all items for the named GPU group (not undoable).        —
-cpuEraseGroupItems              -ceg                     (none)     Evict all items for the named CPU group (not undoable).        —
================================ ======================== ========== ============================================================= =============

For the erase flags, pass item or group names as command objects
(the selection strings).

Return
------

- Size queries (capacity, used, item count, group count): returns a
  single string containing the numeric value in bytes or count.
- Name queries (group names, item names): returns a string array.
- ``-briefText``: returns a single human-readable summary string.
- Edit capacity: returns nothing.
- Edit erase: returns a string containing the count of evicted items.

Example
-------

Python Example:

.. code:: python

   import maya.cmds

   # Query GPU capacity (bytes).
   gpu_cap = maya.cmds.mmImageCache(query=True, gpuCapacity=True)

   # Query CPU memory in use (bytes).
   cpu_used = maya.cmds.mmImageCache(query=True, cpuUsed=True)

   # List all CPU cache group names.
   groups = maya.cmds.mmImageCache(query=True, cpuGroupNames=True)

   # Query item count for a specific CPU group.
   count = maya.cmds.mmImageCache(
       '/path/to/image.####.exr',
       query=True, cpuGroupItemCount=True,
   )

   # Set GPU capacity to 2 GB.
   maya.cmds.mmImageCache(edit=True, gpuCapacity='2147483648')

   # Evict all items belonging to a CPU group.
   maya.cmds.mmImageCache(
       '/path/to/image.####.exr',
       edit=True, cpuEraseGroupItems=True,
   )

MEL Example:

.. code:: text

   // Query GPU capacity.
   string $cap = `mmImageCache -query -gpuCapacity`;

   // List CPU group names.
   string $groups[] = `mmImageCache -query -cpuGroupNames`;

   // Set CPU capacity to 4 GB.
   mmImageCache -edit -cpuCapacity "4294967296";

   // Evict a CPU group.
   mmImageCache -edit -cpuEraseGroupItems "/path/to/image.####.exr";
