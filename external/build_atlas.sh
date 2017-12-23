#!/usr/bin/env bash
# NOTE: This script is for CentOS 6.x, and assumes the base package 'atlas' has
# been installed.
# This script will not "build" ATLAS, but simply copy the libraries from the system location


# Build
# No build is performed.


# Copy
# Atlas headers and libraries.
cp -R --force -t ./external/include /usr/include/atlas-x86_64-base
cp --force -t ./external/include /usr/include/cblas.h
cp --force -t ./external/include /usr/include/clapack.h
cp --force -d -t ./external/lib/ /usr/lib64/atlas/lib*
