# External Archives

This directory is used to store tar/zip files for external
dependencies. The external build scripts use this directory as needed
and sometimes expect files to be added to this directory.

## Autodesk Maya

The following archives may be expected during building and should be
downloaded from [Autodesk](https://www.autodesk.com/):

- Autodesk_Maya_2018_EN_Linux_64bit.tgz
- Autodesk_Maya_2019_Linux_64bit.tgz
- Autodesk_Maya_2020_ML_Linux_64bit.tgz
- Autodesk_Maya_2022_ML_Linux_64bit.tgz
- Autodesk_Maya_2023_ML_Linux_64bit.tgz

## LDPK

A copy of the Lens Distortion Plugin Kit (LDPK) is kept in this
directory, to be used to compile the LDPK library for this project.

The provided archive has been edited from the original to include only
the required source code for the library - all test, documentation and
pre-compiled libraries are removed from the original archive.

- ldpk-2.12.tar

You can get the original copy of the LDPK from the 3DEqualizer website:
https://www.3dequalizer.com/?site=tech_docs&id=110216_01
https://www.3dequalizer.com/user_daten/sections/tech_docs/archives/ldpk-2.12.tgz
