#!/usr/bin/env bash
# Build LevMar library without any dependencies.


# Number of CPUs
CPU_NUM=`nproc --all`


# Clean up
rm -R --force ./external/working/levmar-2.6


# Extract
tar -C ./external/working -xf ./external/archives/levmar-2.6.tgz


# Patch
patch -i ./external/patches/levmar-2.6_nodeps_Makefile.patch ./external/working/levmar-2.6/Makefile
patch -i ./external/patches/levmar-2.6_nodeps_levmar.h.patch ./external/working/levmar-2.6/levmar.h
patch -i ./external/patches/levmar-2.6_nodeps_levmar.h.in.patch ./external/working/levmar-2.6/levmar.h.in


# Build
cd ./external/working/levmar-2.6/
make clean
make liblevmar.a -j${CPU_NUM}
cd ../../../


# Copy
cp --force -t ./external/lib ./external/working/levmar-2.6/liblevmar.a
cp --force -t ./external/include ./external/working/levmar-2.6/levmar.h
