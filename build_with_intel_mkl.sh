#!/usr/bin/env bash
# Builds the Maya plug-in using the Intel MKL libraries.


# Maya directories
MAYA_VERSION=2017
MAYA_INCLUDE_PATH=/usr/autodesk/maya2017/include
MAYA_LIB_PATH=/usr/autodesk/maya2017/lib


# The root of this project.
PROJECT_ROOT=`pwd`

# Where to install the module?
#
# The "$HOME/maya/2017/modules" directory is automatically searched
# for Maya module (.mod) files. Therefore we can install directly.
#
# INSTALL_MODULE_DIR=${PROJECT_ROOT}/modules
INSTALL_MODULE_DIR=~/maya/2017/modules


# Number of CPUs
CPU_NUM=`nproc --all`


# Remove
rm -R --force ${PROJECT_ROOT}/external/lib/lib*.so*
rm -R --force ${PROJECT_ROOT}/external/lib/lib*.a*
rm -R --force ${PROJECT_ROOT}/external/include/*.h*


# Build the external dependencies
bash external/build_mkl.sh
bash external/build_levmar_with_mkl.sh


# Build plugin
mkdir -p build
cd build
rm --force -R *
cmake -DCMAKE_BUILD_TYPE=Release \
      -DCMAKE_INSTALL_PREFIX=${INSTALL_MODULE_DIR} \
      -DUSE_ATLAS=0 \
      -DUSE_MKL=1 \
      -DMAYA_VERSION=${MAYA_VERSION} \
      -DMAYA_INCLUDE_PATH=${MAYA_INCLUDE_PATH} \
      -DMAYA_LIB_PATH=${MAYA_LIB_PATH} \
      -DLEVMAR_LIB_PATH=${PROJECT_ROOT}/external/lib \
      -DLEVMAR_INCLUDE_PATH=${PROJECT_ROOT}/external/include \
      -DMKL_LIB_PATH=${PROJECT_ROOT}/external/lib \
      -DATLAS_LIB_PATH=${PROJECT_ROOT}/external/lib \
      ..
make clean
make -j${CPU_NUM}
make install


# # For developers, make packages ready to distribute to others.
# make package
# make package_source
