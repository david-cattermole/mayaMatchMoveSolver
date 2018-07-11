#!/usr/bin/env bash


# Number of CPUs
CPU_NUM=`nproc --all`


# Clean up
rm -R --force ./external/working/glog-0.3.1/


# Extract
tar -C ./external/working -xf ./external/archives/glog-0.3.1.tar.gz


# Build
cd ./external/working/glog-0.3.1/
./configure
make clean
make -j${CPU_NUM}
# make check  # run tests
cd ../../../


# Copy
mkdir -p ./external/include/glog
cp -d --force -t ./external/lib ./external/working/glog-0.3.1/.libs/lib*.a*
cp -d --force -t ./external/lib ./external/working/glog-0.3.1/.libs/lib*.so*
cp --force -t ./external/include/glog ./external/working/glog-0.3.1/src/glog/*.h


