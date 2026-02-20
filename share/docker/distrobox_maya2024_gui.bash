#!/bin/bash
#
# Distrobox Setup Script for Maya 2024 GUI Runtime Environment
#
# This script creates and configures a Distrobox container with Maya 2024
# for running the Maya GUI on any Linux distribution with X11/Wayland support.
#
# USAGE:
#   1. Ensure you have the Maya 2024 archive in the correct location:
#      ./external/archives/Autodesk_Maya_2024_Linux_64bit.tgz
#
#   2. Run this script from the project root directory:
#      $ cd /path/to/mayaMatchMoveSolver
#      $ bash share/docker/distrobox_maya2024_gui.bash
#
#   3. After setup completes, enter the container:
#      $ distrobox enter maya2024-gui
#
#   4. Inside the container, launch Maya:
#      $ maya
#
#   5. Alternatively, launch Maya directly from your host:
#      $ distrobox enter maya2024-gui -- maya
#
# FEATURES:
#   - Full Maya 2024 GUI support
#   - X11 and Wayland compatibility
#   - NVIDIA GPU acceleration (--nvidia flag)
#   - All required multimedia and graphics libraries
#   - Font support for Maya UI
#
# REQUIREMENTS:
#   - Distrobox installed
#   - Podman or Docker
#   - NVIDIA drivers (if using NVIDIA GPU)
#   - X11 or Wayland display server
#   - Maya 2024 Linux archive (see above)
#
# Maya documentation for installing on RHEL8 / Rocky8:
# https://help.autodesk.com/view/MAYAUL/2024/ENU/?guid=GUID-D2B5433C-E0D2-421B-9BD8-24FED217FD7F
#
# And this forum post:
# https://forums.autodesk.com/t5/maya-forum/install-maya-2023-update-3-on-rocky-linux-8-7-instructions/td-p/11735138

# Configuration
CONTAINER_NAME="maya2024-gui"
IMAGE="rockylinux:8"
MAYA_ARCHIVE="./external/archives/Autodesk_Maya_2024_Linux_64bit.tgz"

echo "--- Initializing Distrobox: $CONTAINER_NAME ---"
DBX_CONTAINER_NAME=podman distrobox create \
                          --image $IMAGE \
                          --name $CONTAINER_NAME \
                          --yes \
                          --nvidia \
                          --init

# Run commands inside the box
dbx_run() {
    distrobox enter $CONTAINER_NAME -- bash -c "$1"
}

echo "--- Installing Extra Packages Enterprise Linux (EPEL) Repository ---"
# Install Extra Packages Enterprise Linux (EPEL) repo for extra tools.
dbx_run "sudo dnf install --assumeyes https://dl.fedoraproject.org/pub/epel/epel-release-latest-8.noarch.rpm"
dbx_run "sudo dnf install --assumeyes epel-release"
dbx_run "sudo dnf update --assumeyes"
dbx_run "sudo dnf makecache"

echo "--- Installing General Packages ---"
dbx_run "sudo dnf install --assumeyes \
    glibc \
    libSM \
    libICE \
    zlib \
    openssl-libs \
    nss \
    libnsl \
    dbus \
    redhat-lsb-core \
    pcre-utf16 \
    pciutils \
    libXdamage"

echo "--- Installing Multimedia Packages ---"
dbx_run "sudo dnf install --assumeyes \
    mesa-libGL \
    mesa-libGL-devel \
    mesa-libGLU \
    mesa-libGLw \
    gamin \
    audiofile-devel \
    e2fsprogs-libs \
    libcap \
    libdrm \
    libmng \
    speech-dispatcher \
    cups \
    libpng15"

echo "--- Installing X Window - Xcb - X11 Packages ---"
# X11/Wayland display server integration packages.
# These ensure proper GUI rendering on both X11 and Wayland with NVIDIA GPU support.
dbx_run "sudo dnf install --assumeyes \
    libX11 \
    libXScrnSaver \
    libXau \
    libXcomposite \
    libXcursor \
    libXext \
    libXfixes \
    libXi \
    libXinerama \
    libXmu \
    libXp \
    libXpm \
    libXrandr \
    libXrender \
    libXt \
    libXtst \
    libxcb \
    libxkbcommon \
    libxkbcommon-x11 \
    libxshmfence \
    xcb-util \
    xcb-util-image \
    xcb-util-keysyms \
    xcb-util-renderutil \
    xcb-util-wm \
    xorg-x11-server-Xorg \
    xorg-x11-server-Xvfb"

echo "--- Installing Font Packages ---"
# Install fonts needed by Maya GUI.
dbx_run "sudo dnf install --assumeyes \
    fontconfig \
    freetype \
    xorg-x11-fonts-ISO8859-1-100dpi \
    xorg-x11-fonts-ISO8859-1-75dpi \
    liberation-mono-fonts \
    liberation-fonts-common \
    liberation-sans-fonts \
    liberation-serif-fonts"

echo "--- Installing OpenGL Packages ---"
# OpenGL libraries for viewport rendering.
# Supports both Mesa (open source) and NVIDIA proprietary drivers.
dbx_run "sudo dnf install --assumeyes \
    mesa-libGLw \
    mesa-libGLU \
    mesa-libGL-devel \
    mesa-libEGL-devel \
    mesa-libGLES-devel \
    mesa-libGLU-devel \
    mesa-libGLw-devel \
    libglvnd \
    libglvnd-opengl \
    libglvnd-egl \
    libglvnd-glx \
    libglvnd-gles \
    libglvnd-core-devel \
    libglvnd-devel"

echo "--- Installing X11/Wayland Compatibility Packages ---"
dbx_run "sudo dnf install --assumeyes \
    alsa-lib \
    gtk3 \
    libX11-xcb \
    libXScrnSaver \
    libxcb \
    qt5-qtbase \
    qt5-qtwayland \
    webkit2gtk3 \
    xcb-util"

echo "--- Installing Maya 2024 ---"
# Install Maya from archive.
if [ -f "$MAYA_ARCHIVE" ]; then
    dbx_run "sudo mkdir -p /temp"
    dbx_run "sudo tar -xf $MAYA_ARCHIVE -C /temp"
    dbx_run "sudo rpm -Uvh /temp/Packages/adsklicensing*.rpm"
    dbx_run "sudo rpm -Uvh /temp/Packages/adskflexnetclient*.rpm"
    dbx_run "sudo rpm -Uvh /temp/Packages/adskflexserver*.rpm"
    dbx_run "sudo rpm -Uvh /temp/Packages/adlmapps*.rpm"
    dbx_run "sudo rpm -Uvh /temp/Packages/Maya2024*.rpm"
    dbx_run "sudo rm -r /temp"
else
    echo "Warning: Maya archive not found at $MAYA_ARCHIVE. Skipping installation."
fi
# echo "--- Configuring Environment Variables ---"

# # Fix the shell syntax errors caused by host function exports.
# dbx_run "echo 'unset -f which module' >> ~/.bashrc.d/distrobox_maya2024.bash"

# # Set Maya Paths.
# dbx_run "echo 'export MAYA_LOCATION=/usr/autodesk/maya/' >> ~/.bashrc.d/distrobox_maya2024.bash"
# dbx_run "echo 'export PATH=\$MAYA_LOCATION/bin:\$PATH' >> ~/.bashrc.d/distrobox_maya2024.bash"

# # Workaround for Maya "Segmentation fault (core dumped)" issue.
# # See https://forums.autodesk.com/t5/maya-general/render-crash-on-linux/m-p/5608552/highlight/true
# dbx_run "echo 'export MAYA_DISABLE_CIP=1' >> ~/.bashrc.d/distrobox_maya2024.bash"

echo ""
echo "===================================================================="
echo "Setup complete!"
echo ""
echo "To enter your Maya GUI environment:"
echo "  $ distrobox enter $CONTAINER_NAME"
echo ""
echo "To launch Maya GUI:"
echo "  Inside container: $ maya"
echo "  From host:        $ QT_QPA_PLATFORM=xcb distrobox enter $CONTAINER_NAME -- maya"
# sudo chown -R $USER:$USER /var/opt/Autodesk/AdskLicensingService
# AdskLicensingService
echo ""
echo "NVIDIA GPU acceleration is enabled via --nvidia flag."
echo "The container supports both X11 and Wayland display servers."
echo "===================================================================="
