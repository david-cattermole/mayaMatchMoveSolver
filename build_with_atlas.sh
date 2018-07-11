#!/usr/bin/env bash


# Use a different CMake
PATH=/opt/jetbrains/clion-2017.3/bin/cmake/bin:${PATH}


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
rm -R --force ${PROJECT_ROOT}/external/include/ceres
rm -R --force ${PROJECT_ROOT}/external/include/Eigen
rm -R --force ${PROJECT_ROOT}/external/include/gflags
rm -R --force ${PROJECT_ROOT}/external/include/glog


# # Build the external dependencies
bash external/build_glog.sh
bash external/build_gflags.sh
bash external/build_atlas.sh
bash external/build_levmar_with_atlas.sh
bash external/build_suitesparse_with_atlas.sh
bash external/build_sparselm_with_atlas.sh
bash external/build_eigen.sh
bash external/build_ceres_with_atlas.sh


# Build plugin
mkdir -p build
cd build
cmake -DCMAKE_BUILD_TYPE=Release \
      -DHAVE_SPLM=1 \
      -DHAVE_CERES=1 \
      -DUSE_SUITE_SPARSE=1 \
      -DUSE_ATLAS=1 \
      -DUSE_MKL=0 \
      -DMAYA_INCLUDE_PATH=${MAYA_INCLUDE_PATH} \
      -DMAYA_LIB_PATH=${MAYA_LIB_PATH} \
      -DLEVMAR_LIB_PATH=${PROJECT_ROOT}/external/lib \
      -DLEVMAR_INCLUDE_PATH=${PROJECT_ROOT}/external/include \
      -DMKL_LIB_PATH=${PROJECT_ROOT}/external/lib \
      -DATLAS_LIB_PATH=${PROJECT_ROOT}/external/lib \
      -DSUITE_SPARSE_LIB_PATH=${PROJECT_ROOT}/external/lib \
      -DSPLM_LIB_PATH=${PROJECT_ROOT}/external/lib \
      -DSPLM_INCLUDE_PATH=${PROJECT_ROOT}/external/lib \
      -DCERES_LIB_PATH=${PROJECT_ROOT}/external/lib \
      -DCERES_INCLUDE_PATH=${PROJECT_ROOT}/external/include \
      ..
make clean
make -j${CPU_NUM}

