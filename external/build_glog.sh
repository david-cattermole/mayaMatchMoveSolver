#!/usr/bin/env bash


# Clean up
rm -R --force ./external/working/glog-0.3.5/


# Extract
tar -C ./external/working -xf ./external/archives/glog-0.3.5.tar.gz


# Build
cd ./external/working/glog-0.3.5/
./configure
make clean
make -j4
# make check  # run tests
cd ../../../


# Copy
mkdir -p ./external/include/glog
cp --force -t ./external/lib ./external/working/glog-0.3.5/.libs/libglog.a
cp --force -t ./external/lib ./external/working/glog-0.3.5/.libs/libglog.so*
cp --force -t ./external/include/glog ./external/working/glog-0.3.5/src/glog/*.h


