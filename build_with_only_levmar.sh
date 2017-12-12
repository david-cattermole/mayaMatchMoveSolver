PROJECT_ROOT=`pwd`


# Remove
rm -R --force ${PROJECT_ROOT}/external/lib/*
rm -R --force ${PROJECT_ROOT}/external/include/*


# Build the external dependencies
sh external/build_levmar_with_nodeps.sh


# Build plugin
mkdir -p build
cd build
rm --force -R *
cmake -DCMAKE_BUILD_TYPE=Release \
      -DMAYA_INCLUDE_PATH=/usr/autodesk/maya2016/include \
      -DMAYA_LIB_PATH=/usr/autodesk/maya2016/lib \
      -DLEVMAR_LIB_PATH=${PROJECT_ROOT}/external/lib \
      -DLEVMAR_INCLUDE_PATH=${PROJECT_ROOT}/external/include \
      -DHAVE_SPLM=0 \
      -DUSE_ATLAS=0 \
      -DUSE_MKL=0 \
      ..
make clean
make -j4

