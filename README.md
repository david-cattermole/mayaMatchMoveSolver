# Maya MatchMove Solver (MM Solver)

An error minimisation solver for MatchMove (MM) related tasks
utilising Maya's DG and DAG architecture, allowing solving of
complex constraints driven by 2D-to-3D re-projection deviation.

## What Is It?

The aim of this project is to provide an minimising non-linear
least squares solver to aid in complex matchmoving tasks
inside Autodesk Maya. This tool is not intended as a
one-click-solution; this tool is for advanced users.

The solver performs [Bundle Adjustment
(BA)](https://en.wikipedia.org/wiki/Bundle_adjustment), solving for 3D
positions (Bundles) of 2D features (Markers) with arbitrary solving
attributes.

Using arbitrary solving attributes makes the solver extremely
flexible; any floating-point attribute in Maya can be adjusted to
reduce 2D-to-3D re-projection error. Use Maya's DG and DAG nodes to
setup complex constraints and find the best solution to any
MatchMove solve you need.

## Releases

The following releases are below. The latest bug-fix version should
always be used, where possible. Forward compatibility is maintained
between point-release versions (v0.1 to v0.2), but major version
releases should be considered major and may introduce breaking
changes.

| Releases                                                                              | Description                                 |
| ------------------------------------------------------------------------------------- | ------------------------------------------- |
| [v0.2.3](https://github.com/david-cattermole/mayaMatchMoveSolver/releases/tag/v0.2.3) | Bug fix release (*recommended*)             |
| [v0.2.2](https://github.com/david-cattermole/mayaMatchMoveSolver/releases/tag/v0.2.2) | Bug fix release                             |
| [v0.2.1](https://github.com/david-cattermole/mayaMatchMoveSolver/releases/tag/v0.2.1) | Bug fix release                             |
| [v0.2.0](https://github.com/david-cattermole/mayaMatchMoveSolver/releases/tag/v0.2.0) | Improved solver and tools                   |
| [v0.1.1](https://github.com/david-cattermole/mayaMatchMoveSolver/releases/tag/v0.1.1) | Bug fix release                             |
| [v0.1.0](https://github.com/david-cattermole/mayaMatchMoveSolver/releases/tag/v0.1.0) | Initial release                             |


## Documentation

For all tutorials, documentation of Tools, Python API and Maya Plug-In
features, take a look at the
[Documentation Home Page](https://david-cattermole.github.io/mayaMatchMoveSolver/).

A copy of the documentation is also installed with *Maya MatchMove
Solver*, you can find it by pressing the *help* button in the Solver
UI, or in the module install directory, for example this path:

(On Windows)
```
C:/Users/<user name>/My Documents/maya/2017/modules/mayaMatchMoveSolver-0.1.0-maya2017-win64/docs/html/index.html
```

## Community

There is a Google Group mailing list, named
 [maya-matchmove-solver](https://groups.google.com/forum/#!forum/maya-matchmove-solver).

The mailing list is a place for user questions and discussions, and
will have release announcements of new versions.

If you find a bug, please report it on the GitHub project
[issues page](https://github.com/david-cattermole/mayaMatchMoveSolver/issues).

## Installation

If you have a 'mayaMatchMoveSolver' archive package and need to
install it, follow the instructions in
[INSTALL.md](https://github.com/david-cattermole/mayaMatchMoveSolver/blob/master/INSTALL.md).

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
