#!/usr/bin/env bash


# Number of CPUs
CPU_NUM=`nproc --all`


# Clean up
rm -R --force ./external/working/gflags-2.2.1/


# Extract
tar -C ./external/working -xf ./external/archives/gflags-2.2.1.tar.gz


# Build
cd ./external/working/gflags-2.2.1/
mkdir build
cd build
cmake ..
make clean
make -j${CPU_NUM}
cd ../../../../


# Copy
cp -R --force -t ./external/lib ./external/working/gflags-2.2.1/build/lib/*
cp -R --force -t ./external/include ./external/working/gflags-2.2.1/build/include/*


