#!/usr/bin/env bash
# Builds the Maya plug-in with levmar.


# Maya directories
MAYA_INCLUDE_PATH=/usr/autodesk/maya/include
MAYA_LIB_PATH=/usr/autodesk/maya/lib


# The root of this project.
PROJECT_ROOT=`pwd`


# Number of CPUs
CPU_NUM=`nproc --all`


# Remove
rm -R --force ${PROJECT_ROOT}/external/lib/lib*.so*
rm -R --force ${PROJECT_ROOT}/external/lib/lib*.a*
rm -R --force ${PROJECT_ROOT}/external/include/*.h*


# Build the external dependencies
bash external/build_levmar_with_nodeps.sh



# Build plugin
mkdir -p build
cd build
rm --force -R *
cmake -DCMAKE_BUILD_TYPE=Release \
      -DUSE_ATLAS=0 \
      -DUSE_MKL=0 \
      -DMAYA_INCLUDE_PATH=${MAYA_INCLUDE_PATH} \
      -DMAYA_LIB_PATH=${MAYA_LIB_PATH} \
      -DLEVMAR_LIB_PATH=${PROJECT_ROOT}/external/lib \
      -DLEVMAR_INCLUDE_PATH=${PROJECT_ROOT}/external/include \
      ..
make clean
make -j${CPU_NUM}

