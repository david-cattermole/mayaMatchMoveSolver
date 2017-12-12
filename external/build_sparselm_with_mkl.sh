# Clean up
rm -R --force ./external/working/sparselm-1.3


# Extract
tar -C ./external/working -xf ./external/archives/sparselm-1.3.tgz


# Patch
patch -i ./external/patches/sparselm-1.3_mkl_Makefile.patch ./external/working/sparselm-1.3/Makefile
patch -i ./external/patches/sparselm-1.3_mkl_Makefile_demo.patch ./external/working/sparselm-1.3/Makefile_demo
patch -i ./external/patches/sparselm-1.3_mkl_solvers.mk.patch ./external/working/sparselm-1.3/solvers.mk


# Build
cd ./external/working/sparselm-1.3/
make clean
make libsplm.a -j4
cd ../../../


# Copy
cp --force -t ./external/lib ./external/working/sparselm-1.3/libsplm.a
cp --force -t ./external/include ./external/working/sparselm-1.3/splm.h

# MKL
cp --force -t ./external/lib/ /opt/intel/mkl/lib/intel64/libmkl_core.so
cp --force -t ./external/lib/ /opt/intel/mkl/lib/intel64/libmkl_def.so
cp --force -t ./external/lib/ /opt/intel/mkl/lib/intel64/libmkl_intel_lp64.so
cp --force -t ./external/lib/ /opt/intel/mkl/lib/intel64/libmkl_gnu_thread.so
