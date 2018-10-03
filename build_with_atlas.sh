#!/usr/bin/env bash
# Build with ATLAS library.


# Maya directories
MAYA_INCLUDE_PATH=/usr/autodesk/maya2017/include
MAYA_LIB_PATH=/usr/autodesk/maya2017/lib


# The root of this project.
PROJECT_ROOT=`pwd`


# Number of CPUs
CPU_NUM=`nproc --all`


# Remove
rm -R --force ${PROJECT_ROOT}/external/lib/lib*.so*
rm -R --force ${PROJECT_ROOT}/external/lib/lib*.a*
rm -R --force ${PROJECT_ROOT}/external/include/*.h*


# Build the external dependencies
bash external/build_atlas.sh
bash external/build_levmar_with_atlas.sh


# Build plugin
mkdir -p build
cd build
rm --force -R *
cmake -DCMAKE_BUILD_TYPE=Release \
      -DUSE_ATLAS=1 \
      -DUSE_MKL=0 \
      -DMAYA_INCLUDE_PATH=${MAYA_INCLUDE_PATH} \
      -DMAYA_LIB_PATH=${MAYA_LIB_PATH} \
      -DLEVMAR_LIB_PATH=${PROJECT_ROOT}/external/lib \
      -DLEVMAR_INCLUDE_PATH=${PROJECT_ROOT}/external/include \
      -DMKL_LIB_PATH=${PROJECT_ROOT}/external/lib \
      -DATLAS_LIB_PATH=${PROJECT_ROOT}/external/lib \
      ..
make clean
make -j${CPU_NUM}

