#!/usr/bin/env bash


# Use a different CMake
# PATH=/opt/clion/clion-2016.3/bin/cmake/bin:${PATH}


# Remove
rm -R --force ./external/lib/*
rm -R --force ./external/include/*


# # Build the external dependencies
bash external/build_glog.sh
bash external/build_gflags.sh
bash external/build_atlas.sh
bash external/build_levmar_with_atlas.sh
bash external/build_suitesparse_with_atlas.sh
bash external/build_sparselm_with_atlas.sh
bash external/build_eigen.sh
bash external/build_ceres_with_atlas.sh


# # Build plugin
# mkdir -p build
# cd build
# cmake -DCMAKE_BUILD_TYPE=Release \
#       -DMAYA_INCLUDE_PATH=/usr/autodesk/maya2016/include \
#       -DMAYA_LIB_PATH=/usr/autodesk/maya2016/lib \
#       -DLEVMAR_LIB_PATH=./external/lib \
#       -DLEVMAR_INCLUDE_PATH=./external/include \
#       -DSPLM_LIB_PATH=./external/lib \
#       -DSPLM_INCLUDE_PATH=./external/lib \
#       -DSUITE_SPARSE_LIB_PATH=./external/lib \
#       -DATLAS_LIB_PATH=/usr/lib64/atlas \
#       -DHAVE_SPLM=1 \
#       -DHAVE_CERES=1 \
#       -DUSE_ATLAS=1 \
#       -DUSE_MKL=0 \
#       ..
# make clean
# make -j4
