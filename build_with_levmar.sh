#!/usr/bin/env bash
# Builds the Maya plug-in with levmar.


# The root of this project.
PROJECT_ROOT=`pwd`


# Remove
rm -R --force ${PROJECT_ROOT}/external/lib/lib*.so*
rm -R --force ${PROJECT_ROOT}/external/lib/lib*.a*
rm -R --force ${PROJECT_ROOT}/external/include/*.h*
rm -R --force ${PROJECT_ROOT}/external/include/ceres
rm -R --force ${PROJECT_ROOT}/external/include/Eigen
rm -R --force ${PROJECT_ROOT}/external/include/gflags
rm -R --force ${PROJECT_ROOT}/external/include/glog


# Build the external dependencies
bash external/build_levmar_with_nodeps.sh


# Build plugin
mkdir -p build
cd build
rm --force -R *
cmake -DCMAKE_BUILD_TYPE=Release \
      -DMAYA_INCLUDE_PATH=/usr/autodesk/maya2016/include \
      -DMAYA_LIB_PATH=/usr/autodesk/maya2016/lib \
      -DLEVMAR_LIB_PATH=${PROJECT_ROOT}/external/lib \
      -DLEVMAR_INCLUDE_PATH=${PROJECT_ROOT}/external/include \
      -DHAVE_SPLM=0 \
      -DHAVE_CERES=0 \
      -DUSE_ATLAS=0 \
      -DUSE_MKL=0 \
      ..
make clean
make -j4

