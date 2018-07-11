#!/usr/bin/env bash

# Number of CPUs
CPU_NUM=`nproc --all`


# Clean up
rm -R --force ./external/working/sparselm-1.3


# Extract
tar -C ./external/working -xf ./external/archives/sparselm-1.3.tgz


# Patch
patch -i ./external/patches/sparselm-1.3_atlas_Makefile.patch ./external/working/sparselm-1.3/Makefile
patch -i ./external/patches/sparselm-1.3_atlas_solvers.mk.patch ./external/working/sparselm-1.3/solvers.mk


# Build
cd ./external/working/sparselm-1.3/
make clean
make libsplm.a -j${CPU_NUM} SUITESPARSE_LIB_PATH=../../../external/lib SUITESPARSE_INCLUDE_DIR=../../../external/include
cd ../../../


# Copy
cp --force -t ./external/lib ./external/working/sparselm-1.3/libsplm.a
cp --force -t ./external/include ./external/working/sparselm-1.3/splm.h
