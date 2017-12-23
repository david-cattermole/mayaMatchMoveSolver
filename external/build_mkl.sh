#!/usr/bin/env bash
# NOTE: This script assumes the Intel MKL is installed at /opt/intel/mkl.
# This script will not "build" MKL, but simply copy the libraries from the system location.


# Build
# No build is performed.


# Copy
cp --force -t ./external/lib/ /opt/intel/mkl/lib/intel64/libmkl_core.so
cp --force -t ./external/lib/ /opt/intel/mkl/lib/intel64/libmkl_def.so
cp --force -t ./external/lib/ /opt/intel/mkl/lib/intel64/libmkl_intel_lp64.so
cp --force -t ./external/lib/ /opt/intel/mkl/lib/intel64/libmkl_mc.so
cp --force -t ./external/lib/ /opt/intel/mkl/lib/intel64/libmkl_sequential.so
cp --force -t ./external/lib/ /opt/intel/mkl/lib/intel64/libmkl_gnu_thread.so
