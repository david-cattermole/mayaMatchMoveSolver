#!/bin/bash
#
# Test script for mmsfm CLI executable.
#
# Run from the project root directory:
#   bash lib/rust/mmcamerasolve-bin/test.bash
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"
OUTPUT_BASE="/tmp/mmcamerasolve-bin_test"

echo "=============================================="
echo "mmsfm CLI Test Script"
echo "=============================================="
echo "Project root: ${PROJECT_ROOT}"
echo "Output directory: ${OUTPUT_BASE}"
echo ""

# Set up environment for building (vcpkg dependencies).
MAYA_VERSION="${MAYA_VERSION:-2024}"
BUILD_DIR_BASE="${BUILD_DIR_BASE:-${PROJECT_ROOT}/..}"
VCPKG_INSTALLED_DIR="${BUILD_DIR_BASE}/build_vcpkg/install/maya${MAYA_VERSION}_linux/x64-linux-dynamic"
if [ -d "${VCPKG_INSTALLED_DIR}" ]; then
    export CHOLMOD_INCLUDE_DIR="${VCPKG_INSTALLED_DIR}/include"
    export CHOLMOD_LIB_DIR="${VCPKG_INSTALLED_DIR}/lib"
    # Set rpath so the test binary finds the shared CHOLMOD libraries.
    export RUSTFLAGS="${RUSTFLAGS:+$RUSTFLAGS }-C link-arg=-Wl,-rpath,${VCPKG_INSTALLED_DIR}/lib"
fi

# Build release version for faster execution.
echo "Building mmcamerasolve-bin (release mode)..."
# cargo build --release -p mmcamerasolve-bin
# cargo build --release -p mmcamerasolve-bin --features visualization
# cargo build --release -p mmcamerasolve-bin --features logging
cargo build --release -p mmcamerasolve-bin --features visualization,logging
echo ""

MM_CAMERA_SOLVE="${PROJECT_ROOT}/target/release/mmcamerasolve"

# Clean output directory.
rm -rf "${OUTPUT_BASE}"
mkdir -p "${OUTPUT_BASE}"

# Test 1: Help output.
echo "----------------------------------------------"
echo "Test 1: Help output"
echo "----------------------------------------------"
${MM_CAMERA_SOLVE} --help
echo ""

# Test 2: Version output.
echo "----------------------------------------------"
echo "Test 2: Version output"
echo "----------------------------------------------"
${MM_CAMERA_SOLVE} --version
echo ""

# Test 3: Cube A dataset (synthetic, clean data).
echo "----------------------------------------------"
echo "Test 3: Cube A dataset"
echo "----------------------------------------------"
UV_FILE="${PROJECT_ROOT}/tests/data/uvtrack/test_cube_a_markers_v1_fmt.uv"
if [ -f "${UV_FILE}" ]; then
    ${MM_CAMERA_SOLVE} "${UV_FILE}" \
        --focal-length 35 \
        --film-back-width 36 \
        --film-back-height 24 \
        --image-width 3600 \
        --image-height 2400 \
        --prefix cube_a \
        --output-dir "${OUTPUT_BASE}" \
        --log-level info
    echo "Output: ${OUTPUT_BASE}"
else
    echo "SKIP: ${UV_FILE} not found"
fi
echo ""

# Test 4: Cube B dataset.
echo "----------------------------------------------"
echo "Test 4: Cube B dataset"
echo "----------------------------------------------"
UV_FILE="${PROJECT_ROOT}/tests/data/uvtrack/test_cube_b_markers_v1_fmt.uv"
if [ -f "${UV_FILE}" ]; then
    ${MM_CAMERA_SOLVE} "${UV_FILE}" \
        --focal-length 35 \
        --film-back-width 36 \
        --film-back-height 24 \
        --image-width 3600 \
        --image-height 2400 \
        --prefix cube_b \
        --output-dir "${OUTPUT_BASE}" \
        --log-level info
    echo "Output: ${OUTPUT_BASE}"
else
    echo "SKIP: ${UV_FILE} not found"
fi
echo ""

# Test 5: stA dataset with mmcamera file input.
echo "----------------------------------------------"
echo "Test 5: stA dataset (mmcamera file input)"
echo "----------------------------------------------"
UV_FILE="${PROJECT_ROOT}/tests/data/uvtrack/stA_v1_format.uv"
MMCAMERA_FILE="${PROJECT_ROOT}/tests/data/mmcamera/stA_copyCamera.mmcamera"
if [ -f "${UV_FILE}" ] && [ -f "${MMCAMERA_FILE}" ]; then
    ${MM_CAMERA_SOLVE} "${UV_FILE}" \
        --mmcamera "${MMCAMERA_FILE}" \
        --prefix stA_mmcamera \
        --output-dir "${OUTPUT_BASE}" \
        --log-level info
    echo "Output: ${OUTPUT_BASE}"
else
    echo "SKIP: ${UV_FILE} or ${MMCAMERA_FILE} not found"
fi
echo ""

# Test 6: stA dataset with nuke lens file.
echo "----------------------------------------------"
echo "Test 6: stA dataset (--nuke-lens)"
echo "----------------------------------------------"
UV_FILE="${PROJECT_ROOT}/tests/data/uvtrack/stA_v1_format.uv"
MMCAMERA_FILE="${PROJECT_ROOT}/tests/data/mmcamera/stA_copyCamera.mmcamera"
NUKE_LENS_FILE="${PROJECT_ROOT}/tests/data/lens_example_files/stA_v001.nk"
if [ -f "${UV_FILE}" ] && [ -f "${MMCAMERA_FILE}" ] && [ -f "${NUKE_LENS_FILE}" ]; then
    ${MM_CAMERA_SOLVE} "${UV_FILE}" \
        --mmcamera "${MMCAMERA_FILE}" \
        --nuke-lens "${NUKE_LENS_FILE}" \
        --prefix stA_nuke_lens \
        --output-dir "${OUTPUT_BASE}" \
        --log-level info
    echo "Output: ${OUTPUT_BASE}"
else
    echo "SKIP: required files not found"
fi
echo ""

# Test 7: stA dataset with v4 UV file (distorted+undistorted data, with lens).
echo "----------------------------------------------"
echo "Test 7: stA dataset (v4 UV with lens undistortion)"
echo "----------------------------------------------"
UV_FILE="${PROJECT_ROOT}/tests/data/uvtrack/stA_with_lens_undistortion.uv"
MMCAMERA_FILE="${PROJECT_ROOT}/tests/data/mmcamera/stA_copyCamera.mmcamera"
NUKE_LENS_FILE="${PROJECT_ROOT}/tests/data/lens_example_files/stA_v001.nk"
if [ -f "${UV_FILE}" ] && [ -f "${MMCAMERA_FILE}" ] && [ -f "${NUKE_LENS_FILE}" ]; then
    ${MM_CAMERA_SOLVE} "${UV_FILE}" \
        --mmcamera "${MMCAMERA_FILE}" \
        --nuke-lens "${NUKE_LENS_FILE}" \
        --prefix stA_undistort \
        --output-dir "${OUTPUT_BASE}" \
        --log-level info
    echo "Output: ${OUTPUT_BASE}"
else
    echo "SKIP: required files not found"
fi
echo ""

# Test 8: stA dataset with v4 UV file without lens file (warning case).
echo "----------------------------------------------"
echo "Test 8: stA dataset (v4 UV without lens, warning expected)"
echo "----------------------------------------------"
UV_FILE="${PROJECT_ROOT}/tests/data/uvtrack/stA_with_lens_undistortion.uv"
MMCAMERA_FILE="${PROJECT_ROOT}/tests/data/mmcamera/stA_copyCamera.mmcamera"
if [ -f "${UV_FILE}" ] && [ -f "${MMCAMERA_FILE}" ]; then
    ${MM_CAMERA_SOLVE} "${UV_FILE}" \
        --mmcamera "${MMCAMERA_FILE}" \
        --prefix stA_no_lens \
        --output-dir "${OUTPUT_BASE}" \
        --log-level info
    echo "Output: ${OUTPUT_BASE}"
else
    echo "SKIP: required files not found"
fi
echo ""

# Test 9: stA dataset with solver settings file.
echo "----------------------------------------------"
echo "Test 9: stA dataset (--solver-settings)"
echo "----------------------------------------------"
UV_FILE="${PROJECT_ROOT}/tests/data/uvtrack/stA_v1_format.uv"
SETTINGS_FILE="${PROJECT_ROOT}/tests/data/mmsettings/solver_settings.mmsettings"
if [ -f "${UV_FILE}" ] && [ -f "${SETTINGS_FILE}" ]; then
    ${MM_CAMERA_SOLVE} "${UV_FILE}" \
        --focal-length 50 \
        --film-back-width 36 \
        --film-back-height 24 \
        --image-width 3600 \
        --image-height 2400 \
        --solver-settings "${SETTINGS_FILE}" \
        --prefix stA_settings \
        --output-dir "${OUTPUT_BASE}" \
        --log-level info
    echo "Output: ${OUTPUT_BASE}"
else
    echo "SKIP: ${UV_FILE} or ${SETTINGS_FILE} not found"
fi
echo ""

# Test 10: stA dataset - with coarse search disabled via mmsettings.
echo "----------------------------------------------"
echo "Test 10: stA dataset (disable value range estimate)"
echo "----------------------------------------------"
UV_FILE="${PROJECT_ROOT}/tests/data/uvtrack/stA_v1_format.uv"
SETTINGS_FILE2="${PROJECT_ROOT}/tests/data/mmsettings/evolution_disable_value_range_estimate.mmsettings"
if [ -f "${UV_FILE}" ] && [ -f "${SETTINGS_FILE2}" ]; then
    ${MM_CAMERA_SOLVE} "${UV_FILE}" \
        --focal-length 50 \
        --film-back-width 36 \
        --film-back-height 24 \
        --image-width 3600 \
        --image-height 2400 \
        --prefix stA \
        --solver evolution_refine \
        --solver-settings "${SETTINGS_FILE2}" \
        --output-dir "${OUTPUT_BASE}" \
        --log-level info
    echo "Output: ${OUTPUT_BASE}"
else
    echo "SKIP: ${UV_FILE} or ${SETTINGS_FILE2} not found"
fi
echo ""

# Test 11: Blasterwalk dataset.
echo "----------------------------------------------"
echo "Test 11: Blasterwalk dataset"
echo "----------------------------------------------"
UV_FILE="${PROJECT_ROOT}/tests/data/uvtrack/blasterwalk_camera_2dtracks_v1_format.uv"
if [ -f "${UV_FILE}" ]; then
    ${MM_CAMERA_SOLVE} "${UV_FILE}" \
        --focal-length 56.4 \
        --film-back-width 36 \
        --film-back-height 20.25 \
        --image-width 3600 \
        --image-height 2025 \
        --solver evolution_refine \
        --prefix blasterwalk \
        --output-dir "${OUTPUT_BASE}" \
        --log-level info
    echo "Output: ${OUTPUT_BASE}"
else
    echo "SKIP: ${UV_FILE} not found"
fi
echo ""

# Test 12: HCW Painting dataset.
echo "----------------------------------------------"
echo "Test 12: HCW Painting dataset"
echo "----------------------------------------------"
UV_FILE="${PROJECT_ROOT}/tests/data/uvtrack/hcw_painting_2dtracks_v1_format.uv"
if [ -f "${UV_FILE}" ]; then
    ${MM_CAMERA_SOLVE} "${UV_FILE}" \
        --focal-length 35 \
        --film-back-width 36 \
        --film-back-height 20.25 \
        --image-width 1920 \
        --image-height 1080 \
        --solver evolution_refine \
        --prefix hcw_painting \
        --output-dir "${OUTPUT_BASE}" \
        --log-level info
    echo "Output: ${OUTPUT_BASE}"
else
    echo "SKIP: ${UV_FILE} not found"
fi
echo ""

# Test 13: Opera House dataset.
echo "----------------------------------------------"
echo "Test 13: Opera House dataset"
echo "----------------------------------------------"
UV_FILE="${PROJECT_ROOT}/tests/data/uvtrack/operahouse_v1_format.uv"
if [ -f "${UV_FILE}" ]; then
    ${MM_CAMERA_SOLVE} "${UV_FILE}" \
        --focal-length 91 \
        --film-back-width 36 \
        --film-back-height 27 \
        --image-width 3072 \
        --image-height 2304 \
        --solver evolution_refine \
        --prefix operahouse \
        --output-dir "${OUTPUT_BASE}" \
        --log-level info
    echo "Output: ${OUTPUT_BASE}"
else
    echo "SKIP: ${UV_FILE} not found"
fi
echo ""

# Test 14: Garage dataset.
echo "----------------------------------------------"
echo "Test 14: Garage dataset"
echo "----------------------------------------------"
UV_FILE="${PROJECT_ROOT}/tests/data/uvtrack/garage_2dtracks_v1_format.uv"
if [ -f "${UV_FILE}" ]; then
    ${MM_CAMERA_SOLVE} "${UV_FILE}" \
        --focal-length 25 \
        --film-back-width 36 \
        --film-back-height 20.25 \
        --image-width 960 \
        --image-height 540 \
        --prefix garage \
        --start-frame 2000 \
        --end-frame 2706 \
        --intermediate-output \
        --output-dir "${OUTPUT_BASE}" \
        --log-level info
    echo "Output: ${OUTPUT_BASE}"
else
    echo "SKIP: ${UV_FILE} not found"
fi
echo ""

# Test 15: Quiet mode.
echo "----------------------------------------------"
echo "Test 15: Quiet mode"
echo "----------------------------------------------"
UV_FILE="${PROJECT_ROOT}/tests/data/uvtrack/test_cube_a_markers_v1_fmt.uv"
if [ -f "${UV_FILE}" ]; then
    ${MM_CAMERA_SOLVE} "${UV_FILE}" \
        --focal-length 35 \
        --film-back-width 36 \
        --film-back-height 24 \
        --image-width 3600 \
        --image-height 2400 \
        --solver evolution_refine \
        --prefix quiet_test \
        --output-dir "${OUTPUT_BASE}"
    echo "Quiet mode completed (no output expected above)"
    echo "Output: ${OUTPUT_BASE}"
else
    echo "SKIP: ${UV_FILE} not found"
fi
echo ""

# Test 16: Frame range override.
echo "----------------------------------------------"
echo "Test 16: Frame range override (frames 1-10)"
echo "----------------------------------------------"
UV_FILE="${PROJECT_ROOT}/tests/data/uvtrack/test_cube_a_markers_v1_fmt.uv"
if [ -f "${UV_FILE}" ]; then
    ${MM_CAMERA_SOLVE} "${UV_FILE}" \
        --focal-length 35 \
        --film-back-width 36 \
        --film-back-height 24 \
        --image-width 3600 \
        --image-height 2400 \
        --start-frame 1 \
        --end-frame 10 \
        --solver evolution_refine \
        --prefix frame_range \
        --output-dir "${OUTPUT_BASE}" \
        --log-level info
    echo "Output: ${OUTPUT_BASE}"
else
    echo "SKIP: ${UV_FILE} not found"
fi
echo ""

# Summary.
echo "=============================================="
echo "Test Summary"
echo "=============================================="
echo "All tests completed!"
# echo ""
# echo "Output files:"
# find "${OUTPUT_BASE}" -name "*.png" -type f 2>/dev/null | sort
echo ""
echo "Total PNG files generated:"
find "${OUTPUT_BASE}" -name "*.png" -type f 2>/dev/null | wc -l
