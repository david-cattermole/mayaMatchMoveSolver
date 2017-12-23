#!/usr/bin/env bash

# Clean up
rm -R --force ./external/working/eigen-eigen-5a0156e40feb/


# Extract
tar -C ./external/working -xf ./external/archives/eigen-eigen-5a0156e40feb.tar.bz2


# Build
# Note: We don't actually build eigen, it's a header-only library.


# Copy
cp -R --force -t ./external/include ./external/working/eigen-eigen-5a0156e40feb/Eigen


