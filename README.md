# Maya MatchMove Solver (MM Solver)

A unique and flexible solver toolset for MatchMove (MM) related tasks
integrated into Autodesk Maya.

The aim of this project is to provide a solver to aid in complex
matchmoving tasks inside Autodesk Maya. This tool is not intended as a
one-click-solution - this tool is for advanced techniques that are
encountered on a daily-basis in the Film and TV industry.

## Documentation

For all tutorials, documentation of Tools, Python API and Maya Plug-In
features, take a look at the
[Documentation Home Page](https://david-cattermole.github.io/mayaMatchMoveSolver/).

The official YouTube channel is
[mmSolver](https://www.youtube.com/channel/UCndLPvFXd9Os7m9sc2Bbbsw),
it contains video tutorials for mmSolver on a range of topics.

A copy of the documentation is also installed with *Maya MatchMove
Solver*, you can find it by pressing the *help* button in the Solver
UI, or in the module install directory, for example this path:

(On Windows)
```
C:/Users/<user name>/My Documents/maya/2017/modules/mayaMatchMoveSolver-0.1.0-maya2018-win64/docs/html/index.html
```

## Community

Do you have a question about mmSolver?
The mailing list is the perfect place to ask!

There is a Google Group mailing list:
[maya-matchmove-solver](https://groups.google.com/forum/#!forum/maya-matchmove-solver).

The mailing list is a place for user questions and discussions, and
will have release announcements of new versions.

If you find a bug, please report it on the GitHub project
[issues page](https://github.com/david-cattermole/mayaMatchMoveSolver/issues).

## Installation

If you have a 'mayaMatchMoveSolver' archive package and need to
install it, follow the instructions in
[INSTALL.md](https://github.com/david-cattermole/mayaMatchMoveSolver/blob/master/INSTALL.md).

## Releases

The following releases are below. The latest bug-fix version should
always be used, where possible. Forward compatibility is maintained
between point-release versions (v0.1 to v0.2), but major version
releases should be considered major and may introduce breaking
changes.

| Releases                                                                                | Description                                        |
|-----------------------------------------------------------------------------------------|----------------------------------------------------|
| [v0.5.7](https://github.com/david-cattermole/mayaMatchMoveSolver/releases/tag/v0.5.7)   | Bug fix for Solver and Ray-cast tools.             |
| [v0.5.6](https://github.com/david-cattermole/mayaMatchMoveSolver/releases/tag/v0.5.6)   | UI window behaviour fixes for Qt 6.x               |
| [v0.5.5](https://github.com/david-cattermole/mayaMatchMoveSolver/releases/tag/v0.5.5)   | Center 2D tool multi-object and component support. |
| [v0.5.4](https://github.com/david-cattermole/mayaMatchMoveSolver/releases/tag/v0.5.4)   | Improve the Solver UI and Camera Solver.           |
| [v0.5.3](https://github.com/david-cattermole/mayaMatchMoveSolver/releases/tag/v0.5.3)   | Change solver validation and world-space bundles.  |
| [v0.5.2](https://github.com/david-cattermole/mayaMatchMoveSolver/releases/tag/v0.5.2)   | Bug fix for Maya 2024+.                            |
| [v0.5.1](https://github.com/david-cattermole/mayaMatchMoveSolver/releases/tag/v0.5.1)   | Support for Maya 2025.                             |
| [v0.5.0](https://github.com/david-cattermole/mayaMatchMoveSolver/releases/tag/v0.5.0)   | Silhouette Renderer and Improved MM ImagePlane.    |
| [v0.4.9](https://github.com/david-cattermole/mayaMatchMoveSolver/releases/tag/v0.4.9)   | Bug fix for Surface Cluster.                       |
| [v0.4.8](https://github.com/david-cattermole/mayaMatchMoveSolver/releases/tag/v0.4.8)   | Add Create Rivet and Surface Cluster tools.        |
| [v0.4.7](https://github.com/david-cattermole/mayaMatchMoveSolver/releases/tag/v0.4.7)   | Bug fix for "Convert to Marker" tool.              |
| [v0.4.6](https://github.com/david-cattermole/mayaMatchMoveSolver/releases/tag/v0.4.6)   | Bug fix for solver and minor features.             |
| [v0.4.5](https://github.com/david-cattermole/mayaMatchMoveSolver/releases/tag/v0.4.5)   | Introduction of MM Renderer and Maya 2024 support. |
| [v0.4.4](https://github.com/david-cattermole/mayaMatchMoveSolver/releases/tag/v0.4.4)   | Solver, 2D Reprojection and Blender-to-3DE fixes.  |
| [v0.4.3](https://github.com/david-cattermole/mayaMatchMoveSolver/releases/tag/v0.4.3)   | Bug fix for performance.                           |
| [v0.4.2](https://github.com/david-cattermole/mayaMatchMoveSolver/releases/tag/v0.4.2)   | Bug fixes and 2D Marker round-tripping.            |
| [v0.4.1](https://github.com/david-cattermole/mayaMatchMoveSolver/releases/tag/v0.4.1)   | Bug fix Basic solver tab.                          |
| [v0.4.0](https://github.com/david-cattermole/mayaMatchMoveSolver/releases/tag/v0.4.0)   | Lens distortion, ImagePlane and Camera Solver.     |
| [v0.3.16](https://github.com/david-cattermole/mayaMatchMoveSolver/releases/tag/v0.3.16) | Maya 2022 support.                                 |
| [v0.3.15](https://github.com/david-cattermole/mayaMatchMoveSolver/releases/tag/v0.3.15) | Added Camera Calibration tool and 3DE R7 support.  |
| [v0.3.14](https://github.com/david-cattermole/mayaMatchMoveSolver/releases/tag/v0.3.14) | Integrated Qt.py and bug fixes.                    |
| [v0.3.13](https://github.com/david-cattermole/mayaMatchMoveSolver/releases/tag/v0.3.13) | New tools, and Maya 2020 support.                  |
| [v0.3.12](https://github.com/david-cattermole/mayaMatchMoveSolver/releases/tag/v0.3.12) | Bug fixes, minor features and updates.             |
| [v0.3.11](https://github.com/david-cattermole/mayaMatchMoveSolver/releases/tag/v0.3.11) | Bug fixes, and minor tool and UI updates.          |
| [v0.3.10](https://github.com/david-cattermole/mayaMatchMoveSolver/releases/tag/v0.3.10) | Bug fix release, support for Mesh Rivets.          |
| [v0.3.9](https://github.com/david-cattermole/mayaMatchMoveSolver/releases/tag/v0.3.9)   | User preferences and minor solver changes.         |
| [v0.3.8](https://github.com/david-cattermole/mayaMatchMoveSolver/releases/tag/v0.3.8)   | Bug fix release.                                   |
| [v0.3.7](https://github.com/david-cattermole/mayaMatchMoveSolver/releases/tag/v0.3.7)   | Performance, stability improvements and bug fixes. |
| [v0.3.6](https://github.com/david-cattermole/mayaMatchMoveSolver/releases/tag/v0.3.6)   | UI Performance Improvements and bug fixes.         |
| [v0.3.5](https://github.com/david-cattermole/mayaMatchMoveSolver/releases/tag/v0.3.5)   | Fixed bugs.                                        |
| [v0.3.4](https://github.com/david-cattermole/mayaMatchMoveSolver/releases/tag/v0.3.4)   | Added Attribute Details and fixed bugs.            |
| [v0.3.3](https://github.com/david-cattermole/mayaMatchMoveSolver/releases/tag/v0.3.3)   | Bug fix release.                                   |
| [v0.3.2](https://github.com/david-cattermole/mayaMatchMoveSolver/releases/tag/v0.3.2)   | Added tools and fixed bugs.                        |
| [v0.3.1](https://github.com/david-cattermole/mayaMatchMoveSolver/releases/tag/v0.3.1)   | Added tools and fixed bugs.                        |
| [v0.3.0](https://github.com/david-cattermole/mayaMatchMoveSolver/releases/tag/v0.3.0)   | Improved solver, GUI and tools                     |
| [v0.2.3](https://github.com/david-cattermole/mayaMatchMoveSolver/releases/tag/v0.2.3)   | Bug fix release                                    |
| [v0.2.2](https://github.com/david-cattermole/mayaMatchMoveSolver/releases/tag/v0.2.2)   | Bug fix release                                    |
| [v0.2.1](https://github.com/david-cattermole/mayaMatchMoveSolver/releases/tag/v0.2.1)   | Bug fix release                                    |
| [v0.2.0](https://github.com/david-cattermole/mayaMatchMoveSolver/releases/tag/v0.2.0)   | Improved solver and tools                          |
| [v0.1.1](https://github.com/david-cattermole/mayaMatchMoveSolver/releases/tag/v0.1.1)   | Bug fix release                                    |
| [v0.1.0](https://github.com/david-cattermole/mayaMatchMoveSolver/releases/tag/v0.1.0)   | Initial release                                    |

## Building

To build (compile) the plug-in follow the steps in
[BUILD.md](https://github.com/david-cattermole/mayaMatchMoveSolver/blob/master/BUILD.md).

## License

*Maya MatchMove Solver* (mmSolver) is licensed under the
[Lesser GNU Public License v3.0](https://github.com/david-cattermole/mayaMatchMoveSolver/blob/master/LICENSE)
or *LGPL-3.0* for short.
This means the project is Free Open Source Software, and will always
stay Free Open Source Software:
[TL;DR](https://www.tldrlegal.com/l/lgpl-3.0).

Please read the *LICENSE* (text) file for details.

## Contributing

If you're interested in contributing to the Maya MatchMove Solver
project, please see the conventions and information in
[DEVELOPER.md](https://github.com/david-cattermole/mayaMatchMoveSolver/blob/master/DEVELOPER.md).

## Bugs or Issues?

All issues are listed in the
[issues page](https://github.com/david-cattermole/mayaMatchMoveSolver/issues)
on the project page. If you have found a bug, please submit an issue and we will
try to address it as soon as possible.
