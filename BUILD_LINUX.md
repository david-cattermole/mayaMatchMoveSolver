# Building on Linux

We can build `mmSolver` on Linux quite easily using the provided
[Docker](https://www.docker.com/) containers. Using the Docker
containers you are also able to build on a Microsoft Windows host with
[Windows Subsystem for Linux](https://docs.microsoft.com/en-us/windows/wsl/)
installed.

As part of the Docker build process Autodesk Maya is automatically
installed. You must provide a valid Maya installation archive for
Linux, such as "Autodesk_Maya_2019_Linux_64bit.tgz", located in the
`<project root>/external/archives`. The Docker scripts will
automatically install Maya inside the Docker image.

On a Linux (or Windows) host Bash or Power Shell terminal, run:
```commandline
$ cd <project root>
$ docker build --file share/docker/Dockerfile_mayaXXXX -t mmsolver-linux-mayaXXXX-build .
$ docker run --rm --interactive --volume "${pwd}:/mmSolver" --tty mmsolver-linux-mayaXXXX-build bash

# Inside the docker container
$ ./scripts/build_mmSolver_linux_mayaXXXX.bash
```

Note: Replace XXXX, with the Maya version to build for.

Note: The host computer should have 10GB (or more) storage space
available to build with Docker.

The sections below explain the process in more detail.

# Building Dependencies

mmSolver has a few dependencies, and are listed in
[BUILD.md](https://github.com/david-cattermole/mayaMatchMoveSolver/blob/master/BUILD.md#dependencies).

The third-party dependencies are downloaded and built for
mmSolver automatically using the standard build script
`<project root>/scripts/build_mmSolver_linux_mayaXXXX.bash`
(see below).

Using the CMake configuration, you can override the third-party
dependencies Git repositories URLs as needed - use `cmake-gui` to see
and configure the CMake variables.

# Build mmSolver

Run these commands, on Linux:
```commandline
$ cd <project root>
$ make build_XXXX

# Run tests (optional, but encouraged)
$ cd <project root>
$ /usr/autodesk/mayaVERSION/bin/mayapy tests/runTests.py
```

Note: Replace XXXX, with the Maya version to build for.

Following the steps above you will have the Maya plug-in compiled, and
installed into your `~/maya/MAYA_VERSION/modules` directory.

# Customizing Build Location

By default, mmSolver will build in the directory `${PROJECT_ROOT}/..`
(the parent directory of your project root). You can override this
location by setting the `BUILD_DIR_BASE` environment variable before
running the build script:

```bash
# Set a custom build directory
$ export BUILD_DIR_BASE=/path/to/custom/build/directory
$ ./scripts/build_mmSolver_linux_maya2024.bash

# Or set it inline with the build command
$ BUILD_DIR_BASE=/path/to/custom/build/directory ./scripts/build_mmSolver_linux_maya2024.bash
```

Setting a custom build directory can be useful when:

- You want to keep build files on a different disk partition.
- You're building multiple versions and want separate build
  directories.
- You have limited space in the default location.

# Run Test Suite

After all parts of the `mmSolver` are installed and can be found by
Maya, try running the test suite to confirm everything is working as
expected.

On Linux:
```commandline
$ cd <project root>
$ make test_VERSION

# Or run tests directly with mayapy.
$ /usr/autodesk/mayaVERSION/bin/mayapy tests/runTests.py
```

Make sure you use the same Maya version 'mayapy' for testing as you
have build for.

For more information about testing, see the Testing section in
[DEVELOPER.md](https://github.com/david-cattermole/mayaMatchMoveSolver/blob/master/DEVELOPER.md).

# Build Release Packages from Scratch

NOTE: It is recommended to use the Docker containers for building
mmSolver (and dependencies) as described above. Using Docker will
produce the exact same packages, but in a reproducible recipe and
without polluting the developer's host computer.

If you wish to build a (.tar.gz) package for users to download, there
are a number of steps to ensure are run correctly in specific
environments. The commands below are one-liner commands to set up
everything from scratch and build, then package ready for
distribution.

Run in the Linux Bash terminal:
```commandline
# Maya 2016
$ source load_maya2016.sh  # Example script to set up development environment (not provided).
$ mkdir -p /media/dev/mayaMatchMoveSolver_maya2016Deploy_linux ; cd /media/dev/ ; git clone git@github.com:david-cattermole/mayaMatchMoveSolver.git mayaMatchMoveSolver_maya2016Deploy_linux
$ cd /media/dev/mayaMatchMoveSolver_maya2016Deploy_linux ; git fetch --all; git checkout -f develop; git pull ; rm -R --force build_* ; rm -R --force external/install/* ; rm -R --force external/working/*/ ; bash scripts/build_mmSolver_linux_maya2016.bash

# Maya 2017
$ source load_maya2017.sh  # Example script to set up development environment (not provided).
$ mkdir -p /media/dev/mayaMatchMoveSolver_maya2017Deploy_linux ; cd /media/dev/ ; git clone git@github.com:david-cattermole/mayaMatchMoveSolver.git mayaMatchMoveSolver_maya2017Deploy_linux
$ cd /media/dev/mayaMatchMoveSolver_maya2017Deploy_linux ; git fetch --all; git checkout -f develop; git pull ; rm -R --force build_* ; rm -R --force external/install/* ; rm -R --force external/working/*/ ; bash scripts/build_mmSolver_linux_maya2017.bash

# Maya 2018
$ source load_maya2018.sh  # Example script to set up development environment (not provided).
$ mkdir -p /media/dev/mayaMatchMoveSolver_maya2018Deploy_linux ; cd /media/dev/ ; git clone git@github.com:david-cattermole/mayaMatchMoveSolver.git mayaMatchMoveSolver_maya2018Deploy_linux
$ cd /media/dev/mayaMatchMoveSolver_maya2018Deploy_linux ; git fetch --all; git checkout -f develop; git pull ; rm -R --force build_* ; rm -R --force external/install/* ; rm -R --force external/working/*/ ; bash scripts/build_mmSolver_linux_maya2018.bash

# Maya 2019
$ source load_maya2019.sh  # Example script to set up development environment (not provided).
$ mkdir -p /media/dev/mayaMatchMoveSolver_maya2019Deploy_linux ; cd /media/dev/ ; git clone git@github.com:david-cattermole/mayaMatchMoveSolver.git mayaMatchMoveSolver_maya2019Deploy_linux
$ cd /media/dev/mayaMatchMoveSolver_maya2019Deploy_linux ; git fetch --all; git checkout -f develop; git pull; rm -R --force build_* ; rm -R --force external/install/* ; rm -R --force external/working/*/ ; bash scripts/build_mmSolver_linux_maya2019.bash

# Maya 2020
$ source load_maya2020.sh  # Example script to set up development environment (not provided).
$ mkdir -p /media/dev/mayaMatchMoveSolver_maya2020Deploy_linux ; cd /media/dev/ ; git clone git@github.com:david-cattermole/mayaMatchMoveSolver.git mayaMatchMoveSolver_maya2020Deploy_linux
$ cd /media/dev/mayaMatchMoveSolver_maya2020Deploy_linux ; git fetch --all; git checkout -f develop; git pull; rm -R --force build_* ; rm -R --force external/install/* ; rm -R --force external/working/*/ ; bash scripts/build_mmSolver_linux_maya2020.bash

# Maya 2022
$ source load_maya2022.sh  # Example script to set up development environment (not provided).
$ mkdir -p /media/dev/mayaMatchMoveSolver_maya2022Deploy_linux ; cd /media/dev/ ; git clone git@github.com:david-cattermole/mayaMatchMoveSolver.git mayaMatchMoveSolver_maya2022Deploy_linux
$ cd /media/dev/mayaMatchMoveSolver_maya2022Deploy_linux ; git fetch --all; git checkout -f develop; git pull; rm -R --force build_* ; rm -R --force external/install/* ; rm -R --force external/working/*/ ; bash scripts/build_mmSolver_linux_maya2022.bash

# Maya 2023
$ source load_maya2023.sh  # Example script to set up development environment (not provided).
$ mkdir -p /media/dev/mayaMatchMoveSolver_maya2023Deploy_linux ; cd /media/dev/ ; git clone git@github.com:david-cattermole/mayaMatchMoveSolver.git mayaMatchMoveSolver_maya2023Deploy_linux
$ cd /media/dev/mayaMatchMoveSolver_maya2023Deploy_linux ; git fetch --all; git checkout -f develop; git pull; rm -R --force build_* ; rm -R --force external/install/* ; rm -R --force external/working/*/ ; bash scripts/build_mmSolver_linux_maya2023.bash

# Maya 2024
$ source load_maya2024.sh  # Example script to set up development environment (not provided).
$ mkdir -p /media/dev/mayaMatchMoveSolver_maya2024Deploy_linux ; cd /media/dev/ ; git clone git@github.com:david-cattermole/mayaMatchMoveSolver.git mayaMatchMoveSolver_maya2024Deploy_linux
$ cd /media/dev/mayaMatchMoveSolver_maya2024Deploy_linux ; git fetch --all; git checkout -f develop; git pull; rm -R --force build_* ; rm -R --force external/install/* ; rm -R --force external/working/*/ ; bash scripts/build_mmSolver_linux_maya2024.bash
```

Package files can then be uploaded from the
"~/dev/mayaMatchMoveSolver_maya*Deploy_linux/packages" folder.

NOTE: The directories above are hard-coded for the author's
environment, you may need to change the paths for your environment.
