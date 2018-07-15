#!/usr/bin/env bash
# NOTE: This script is for CentOS 7.x, and assumes the base packages 'atlas',
# 'lapack' and 'blas' has been installed.
#
# This script will not "build" ATLAS, but simply copy the libraries from the
# system location


# Build
# No build is performed.


# Copy
# Atlas headers and libraries.
cp -R --force -t ./external/include /usr/include/atlas-x86_64-base
cp --force -t ./external/include /usr/include/cblas.h
cp --force -t ./external/include /usr/include/clapack.h
cp --force -d -t ./external/lib/ /usr/lib64/atlas/lib*
cp --force -d -t ./external/lib/ /usr/lib64/lib*lapack*
cp --force -d -t ./external/lib/ /usr/lib64/libblas*
cp --force -d -t ./external/lib/ /usr/lib64/libblas64*
