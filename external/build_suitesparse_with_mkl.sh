#!/usr/bin/env bash

# Clean up
rm -R --force ./external/working/SuiteSparse/


# Extract
tar -C ./external/working -xf ./external/archives/SuiteSparse-5.0.0.tar.gz


# Build
cd ./external/working/SuiteSparse/
make distclean
make library -j4 \
     AUTOCC=no \
     MKLROOT=/opt/intel/mkl/ \
     BLAS='-L/opt/intel/mkl/lib/intel64 -Wl,--no-as-needed -lmkl_intel_lp64 -lmkl_core -lmkl_gnu_thread -lgomp -lpthread -lm -ldl' \
     LAPACK=''
cd ../../../


# Copy
cp --force -t ./external/lib ./external/working/SuiteSparse/lib/lib*
cp --force -t ./external/include ./external/working/SuiteSparse/include/*.h


