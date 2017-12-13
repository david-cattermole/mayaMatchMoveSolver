#!/usr/bin/env bash

# Clean up
rm -R --force ./external/working/levmar-2.6/

# Extract
tar -C ./external/working -xf ./external/archives/levmar-2.6.tgz

# Patch
patch -i ./external/patches/levmar-2.6_mkl_Makefile.patch ./external/working/levmar-2.6/Makefile

# Build
cd ./external/working/levmar-2.6/
make clean
make -j4
cd ../../../

# Copy
cp --force -t ./external/lib ./external/working/levmar-2.6/liblevmar.a
cp --force -t ./external/include ./external/working/levmar-2.6/levmar.h

# MKL
cp --force -t ./external/lib/ /opt/intel/mkl/lib/intel64/libmkl_core.so
cp --force -t ./external/lib/ /opt/intel/mkl/lib/intel64/libmkl_def.so
cp --force -t ./external/lib/ /opt/intel/mkl/lib/intel64/libmkl_intel_lp64.so
cp --force -t ./external/lib/ /opt/intel/mkl/lib/intel64/libmkl_mc.so
cp --force -t ./external/lib/ /opt/intel/mkl/lib/intel64/libmkl_sequential.so
