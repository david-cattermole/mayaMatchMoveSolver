#!/usr/bin/env bash


# Number of CPUs
CPU_NUM=`nproc --all`


# Clean up
rm -R --force ./external/working/ceres-solver-1.13.0/


# Extract
tar -C ./external/working -xf ./external/archives/ceres-solver-1.13.0.tar.gz


# Build
cd ./external/working/ceres-solver-1.13.0/
make clean
mkdir build
cd build
# Note: Using 'EIGENSPARSE=ON' turns Ceres Solver into LGPL licensed.
cmake \
    -DBUILD_EXAMPLES=ON \
    -DBUILD_SHARED_LIBS=ON \
    -DBUILD_TESTING=ON \
    -DCXX11=OFF \
    -DEXPORT_BUILD_DIR=OFF \
    -DMINIGLOG=OFF \
    -DOPENMP=OFF \
    -DSCHUR_SPECIALIZATIONS=ON \
    -DGLOG=ON \
    -Dglog_DIR=../../../../external \
    -DGLOG_INCLUDE_DIR=../../../../external/include \
    -DGLOG_LIBRARY=../../../../external/lib/libglog.so \
    -DGFLAGS=ON \
    -Dgflags_DIR=../../../../external/include \
    -DCUSTOM_BLAS=ON \
    -DBLAS_blas_LIBRARY='BLAS_blas_LIBRARY-NOTFOUND' \
    -DBLAS_mkl_core_LIBRARY=../../../../external/lib/libmkl_core.so \
    -DBLAS_mkl_intel_lp64_LIBRARY=../../../../external/lib/libmkl_intel_lp64.so \
    -DBLAS_mkl_intel_thread_LIBRARY=../../../../external/lib/libmkl_intel_thread.so \
    -DBLAS_mkl_sequential_LIBRARY=../../../../external/lib/libmkl_sequential.so \
    -DLAPACK=ON \
    -DLAPACK_lapack_LIBRARY='LAPACK_lapack_LIBRARY-NOTFOUND' \
    -DLAPACK_lapack_LIBRARY=../../../../external/lib/libmkl_gf_lp64.so \
    -DSUITESPARSE=ON \
    -DAMD_INCLUDE_DIR=../../../../external/include \
    -DAMD_LIBRARY=../../../../external/lib/libamd.so \
    -DCAMD_INCLUDE_DIR=../../../../external/include \
    -DCAMD_LIBRARY=../../../../external/lib/libcamd.so \
    -DCCOLAMD_INCLUDE_DIR=../../../../external/include \
    -DCCOLAMD_LIBRARY=../../../../external/lib/libcolamd.so \
    -DCHOLMOD_INCLUDE_DIR=../../../../external/include \
    -DCHOLMOD_LIBRARY=../../../../external/lib/libcholmod.so \
    -DCOLAMD_INCLUDE_DIR=../../../../external/include \
    -DCOLAMD_LIBRARY=../../../../external/lib/libcolamd.so \
    -DCXSPARSE=ON \
    -DCXSPARSE_INCLUDE_DIR=../../../../external/include \
    -DCXSPARSE_LIBRARY=../../../../external/lib/libcxsparse.so \
    -DMETRIS_LIBRARY=../../../../external/lib/libmetris.so \
    -DSUITESPARSE_CONFIG_INCLUDE_DIR=../../../../external/include \
    -DSUITESPARSE_CONFIG_LIBRARY=../../../../external/lib/libsuitesparseconfig.so \
    -DSUITESPARSEQR_INCLUDE_DIR=../../../../external/include \
    -DSUITESPARSEQR_LIBRARY=../../../../external/lib/libspqr.so \
    -DEIGENSPARSE=ON \
    -DEIGEN_INCLUDE_DIR=../../../../external/include \
    -DEigen3_DIR=../../../../external/include \
    ..
make -j${CPU_NUM}
cd ../../../../


# Copy
cp --force -d -t ./external/lib ./external/working/ceres-solver-1.13.0/build/lib/lib*
cp -R --force -t ./external/include ./external/working/ceres-solver-1.13.0/include/ceres

