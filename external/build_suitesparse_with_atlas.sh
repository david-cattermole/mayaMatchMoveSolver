#!/usr/bin/env bash
# NOTE: This script is for CentOS 6.x, and assumes the base package 'atlas' has
# been installed.

# Number of CPUs
CPU_NUM=`nproc --all`


# Clean up
rm -R --force ./external/working/SuiteSparse/


# Extract
tar -C ./external/working -xf ./external/archives/SuiteSparse-5.0.0.tar.gz


# Build
cd ./external/working/SuiteSparse/
make distclean
make library -j${CPU_NUM} \
     CFOPENMP='' \
     AUTOCC=no \
     BLAS='-L/usr/lib64/atlas -lcblas -lf77blas' \
     LAPACK='-L/usr/lib64/atlas -lclapack -llapack -latlas'
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
