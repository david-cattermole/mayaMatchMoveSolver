# Icons

The icons used in mmSolver are contained in this directory.

The "edit/" sub-directory contain the editable files, used to create the icons.

## Guidelines

The icons in mmSolver should:
- be readable and obvious to users.
- be consistent and share a common language with all other icons in
  mmSolver (and in Autodesk Maya).
- be defined in vector formats whenever possible (to allow rendering
  bitmaps at higher resolutions for Hi-DPI screens).
- use open standard formats (like SVG format) where possible to avoid
  proprietary formats and avoid vendor lock-in.

Note: [Inkscape](https://inkscape.org/) is a really good Free Software
for creating vector artwork icons - it is recommended to use it for
creating the icons for mmSolver.

## Shelf Icon Naming Conventions

Icons for Maya shelf buttons require the following naming convention:
```
name.png      # The default 32x32 icon.
name_150.png  # The 150% 48x48 icon.
name_200.png  # The 200% 64x64 icon.
```

Please see [High resolution shelf
icons](https://help.autodesk.com/view/MAYAUL/2025/ENU/?guid=GUID-F2900709-59D3-4E67-A217-4FECC84053BE)
for more details.

## Node Icon Naming Conventions

Icons for Maya nodes in the Autodesk Maya Outliner require the
following naming convention:
```
out_nodeType.png
```

Additionally the icons must have a resolution of 20x20.

## Building Icons

To speed up the process of outputting the bitmap icons with the
correct naming convention and resolution, there is a script (currently
only on Windows) to automate the process.

This uses [Inkscape](https://inkscape.org/) to render the SVG icons
into PNG files.

On Windows:
```cmd
:: Go to root of the icons directory.
> CD <project root>\share/icons/

:: Runs Inkscape for all files and exports all PNG/SVG files.
> build_icons.bat
```
