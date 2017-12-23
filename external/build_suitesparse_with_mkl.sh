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
cp --force -d -t ./external/lib ./external/working/SuiteSparse/lib/lib*
cp --force -d -t ./external/lib ./external/working/SuiteSparse/AMD/Lib/lib*
cp --force -d -t ./external/lib ./external/working/SuiteSparse/BTF/Lib/lib*
cp --force -d -t ./external/lib ./external/working/SuiteSparse/CAMD/Lib/lib*
cp --force -d -t ./external/lib ./external/working/SuiteSparse/CCOLAMD/Lib/lib*
cp --force -d -t ./external/lib ./external/working/SuiteSparse/CHOLMOD/Lib/lib*
cp --force -d -t ./external/lib ./external/working/SuiteSparse/CSparse/Lib/lib*
cp --force -d -t ./external/lib ./external/working/SuiteSparse/CXSparse/Lib/lib*
cp --force -d -t ./external/lib ./external/working/SuiteSparse/KLU/Lib/lib*
cp --force -d -t ./external/lib ./external/working/SuiteSparse/LDL/Lib/lib*
cp --force -d -t ./external/lib ./external/working/SuiteSparse/RBio/Lib/lib*
cp --force -d -t ./external/lib ./external/working/SuiteSparse/SPQR/Lib/lib*
cp --force -d -t ./external/lib ./external/working/SuiteSparse/SuiteSparse_config/lib*
cp --force -d -t ./external/lib ./external/working/SuiteSparse/UMFPACK/Lib/lib*

cp --force -t ./external/include ./external/working/SuiteSparse/include/*.h*
cp --force -t ./external/include ./external/working/SuiteSparse/AMD/Include/*.h*
cp --force -t ./external/include ./external/working/SuiteSparse/BTF/Include/*.h*
cp --force -t ./external/include ./external/working/SuiteSparse/CAMD/Include/*.h*
cp --force -t ./external/include ./external/working/SuiteSparse/CCOLAMD/Include/*.h*
cp --force -t ./external/include ./external/working/SuiteSparse/CHOLMOD/Include/*.h*
cp --force -t ./external/include ./external/working/SuiteSparse/CSparse/Include/*.h*
cp --force -t ./external/include ./external/working/SuiteSparse/CXSparse/Include/*.h*
cp --force -t ./external/include ./external/working/SuiteSparse/KLU/Include/*.h*
cp --force -t ./external/include ./external/working/SuiteSparse/LDL/Include/*.h*
cp --force -t ./external/include ./external/working/SuiteSparse/RBio/Include/*.h*
cp --force -t ./external/include ./external/working/SuiteSparse/SPQR/Include/*.h*
cp --force -t ./external/include ./external/working/SuiteSparse/SuiteSparse_config/*.h*
cp --force -t ./external/include ./external/working/SuiteSparse/UMFPACK/Include/*.h*
