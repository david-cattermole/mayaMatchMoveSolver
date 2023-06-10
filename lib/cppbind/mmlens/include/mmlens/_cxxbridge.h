#pragma once
#include <array>
#include <cstdint>
#include <type_traits>

#include "mmlens/_cxx.h"
#include "mmlens/_symbol_export.h"

namespace mmlens {
enum class DistortionDirection : ::std::uint8_t;
enum class LensModelState : ::std::uint8_t;
enum class LensModelType : ::std::uint8_t;
struct CameraParameters;
struct LensParameters;
struct TdeClassicParameters;
struct TdeRadialDecenteredDeg4CylindricParameters;
struct TdeAnamorphicDeg4RotateSqueezeXYParameters;
struct TdeAnamorphicDeg4RotateSqueezeXYRescaledParameters;
}  // namespace mmlens

namespace mmlens {
#ifndef CXXBRIDGE1_ENUM_mmlens$DistortionDirection
#define CXXBRIDGE1_ENUM_mmlens$DistortionDirection
enum class DistortionDirection : ::std::uint8_t {
    kUndistort = 0,
    kRedistort = 1,
    kNumDistortionDirection = 2,
};
#endif  // CXXBRIDGE1_ENUM_mmlens$DistortionDirection

#ifndef CXXBRIDGE1_ENUM_mmlens$LensModelState
#define CXXBRIDGE1_ENUM_mmlens$LensModelState
enum class LensModelState : ::std::uint8_t {
    kUninitialized = 0,
    kClean = 1,
    kDirty = 2,
    kNumLensModelState = 3,
};
#endif  // CXXBRIDGE1_ENUM_mmlens$LensModelState

#ifndef CXXBRIDGE1_ENUM_mmlens$LensModelType
#define CXXBRIDGE1_ENUM_mmlens$LensModelType
enum class LensModelType : ::std::uint8_t {
    kUninitialized = 0,
    kPassthrough = 1,
    k3deClassic = 2,
    k3deRadialStdDeg4 = 3,
    k3deAnamorphicStdDeg4 = 4,
    k3deAnamorphicStdDeg4Rescaled = 5,
    kNumLensModelType = 6,
};
#endif  // CXXBRIDGE1_ENUM_mmlens$LensModelType

#ifndef CXXBRIDGE1_STRUCT_mmlens$CameraParameters
#define CXXBRIDGE1_STRUCT_mmlens$CameraParameters
struct CameraParameters final {
    double focal_length_cm;
    double film_back_width_cm;
    double film_back_height_cm;
    double pixel_aspect;
    double lens_center_offset_x_cm;
    double lens_center_offset_y_cm;

    bool operator==(const CameraParameters &) const noexcept;
    bool operator!=(const CameraParameters &) const noexcept;
    bool operator<(const CameraParameters &) const noexcept;
    bool operator<=(const CameraParameters &) const noexcept;
    bool operator>(const CameraParameters &) const noexcept;
    bool operator>=(const CameraParameters &) const noexcept;
    using IsRelocatable = ::std::true_type;
};
#endif  // CXXBRIDGE1_STRUCT_mmlens$CameraParameters

#ifndef CXXBRIDGE1_STRUCT_mmlens$LensParameters
#define CXXBRIDGE1_STRUCT_mmlens$LensParameters
struct LensParameters final {
    ::mmlens::LensModelType mode;
    ::std::array<double, 5> values;

    using IsRelocatable = ::std::true_type;
};
#endif  // CXXBRIDGE1_STRUCT_mmlens$LensParameters

#ifndef CXXBRIDGE1_STRUCT_mmlens$TdeClassicParameters
#define CXXBRIDGE1_STRUCT_mmlens$TdeClassicParameters
struct TdeClassicParameters final {
    double distortion;
    double anamorphic_squeeze;
    double curvature_x;
    double curvature_y;
    double quartic_distortion;

    bool operator==(const TdeClassicParameters &) const noexcept;
    bool operator!=(const TdeClassicParameters &) const noexcept;
    bool operator<(const TdeClassicParameters &) const noexcept;
    bool operator<=(const TdeClassicParameters &) const noexcept;
    bool operator>(const TdeClassicParameters &) const noexcept;
    bool operator>=(const TdeClassicParameters &) const noexcept;
    using IsRelocatable = ::std::true_type;
};
#endif  // CXXBRIDGE1_STRUCT_mmlens$TdeClassicParameters

#ifndef CXXBRIDGE1_STRUCT_mmlens$TdeRadialDecenteredDeg4CylindricParameters
#define CXXBRIDGE1_STRUCT_mmlens$TdeRadialDecenteredDeg4CylindricParameters
struct TdeRadialDecenteredDeg4CylindricParameters final {
    double degree2_distortion;
    double degree2_u;
    double degree2_v;
    double degree4_distortion;
    double degree4_u;
    double degree4_v;
    double cylindric_direction;
    double cylindric_bending;

    bool operator==(
        const TdeRadialDecenteredDeg4CylindricParameters &) const noexcept;
    bool operator!=(
        const TdeRadialDecenteredDeg4CylindricParameters &) const noexcept;
    bool operator<(
        const TdeRadialDecenteredDeg4CylindricParameters &) const noexcept;
    bool operator<=(
        const TdeRadialDecenteredDeg4CylindricParameters &) const noexcept;
    bool operator>(
        const TdeRadialDecenteredDeg4CylindricParameters &) const noexcept;
    bool operator>=(
        const TdeRadialDecenteredDeg4CylindricParameters &) const noexcept;
    using IsRelocatable = ::std::true_type;
};
#endif  // CXXBRIDGE1_STRUCT_mmlens$TdeRadialDecenteredDeg4CylindricParameters

#ifndef CXXBRIDGE1_STRUCT_mmlens$TdeAnamorphicDeg4RotateSqueezeXYParameters
#define CXXBRIDGE1_STRUCT_mmlens$TdeAnamorphicDeg4RotateSqueezeXYParameters
struct TdeAnamorphicDeg4RotateSqueezeXYParameters final {
    double degree2_cx02;
    double degree2_cy02;
    double degree2_cx22;
    double degree2_cy22;
    double degree4_cx04;
    double degree4_cy04;
    double degree4_cx24;
    double degree4_cy24;
    double degree4_cx44;
    double degree4_cy44;
    double lens_rotation;
    double squeeze_x;
    double squeeze_y;

    bool operator==(
        const TdeAnamorphicDeg4RotateSqueezeXYParameters &) const noexcept;
    bool operator!=(
        const TdeAnamorphicDeg4RotateSqueezeXYParameters &) const noexcept;
    bool operator<(
        const TdeAnamorphicDeg4RotateSqueezeXYParameters &) const noexcept;
    bool operator<=(
        const TdeAnamorphicDeg4RotateSqueezeXYParameters &) const noexcept;
    bool operator>(
        const TdeAnamorphicDeg4RotateSqueezeXYParameters &) const noexcept;
    bool operator>=(
        const TdeAnamorphicDeg4RotateSqueezeXYParameters &) const noexcept;
    using IsRelocatable = ::std::true_type;
};
#endif  // CXXBRIDGE1_STRUCT_mmlens$TdeAnamorphicDeg4RotateSqueezeXYParameters

#ifndef CXXBRIDGE1_STRUCT_mmlens$TdeAnamorphicDeg4RotateSqueezeXYRescaledParameters
#define CXXBRIDGE1_STRUCT_mmlens$TdeAnamorphicDeg4RotateSqueezeXYRescaledParameters
struct TdeAnamorphicDeg4RotateSqueezeXYRescaledParameters final {
    double degree2_cx02;
    double degree2_cy02;
    double degree2_cx22;
    double degree2_cy22;
    double degree4_cx04;
    double degree4_cy04;
    double degree4_cx24;
    double degree4_cy24;
    double degree4_cx44;
    double degree4_cy44;
    double lens_rotation;
    double squeeze_x;
    double squeeze_y;
    double rescale;

    bool operator==(const TdeAnamorphicDeg4RotateSqueezeXYRescaledParameters &)
        const noexcept;
    bool operator!=(const TdeAnamorphicDeg4RotateSqueezeXYRescaledParameters &)
        const noexcept;
    bool operator<(const TdeAnamorphicDeg4RotateSqueezeXYRescaledParameters &)
        const noexcept;
    bool operator<=(const TdeAnamorphicDeg4RotateSqueezeXYRescaledParameters &)
        const noexcept;
    bool operator>(const TdeAnamorphicDeg4RotateSqueezeXYRescaledParameters &)
        const noexcept;
    bool operator>=(const TdeAnamorphicDeg4RotateSqueezeXYRescaledParameters &)
        const noexcept;
    using IsRelocatable = ::std::true_type;
};
#endif  // CXXBRIDGE1_STRUCT_mmlens$TdeAnamorphicDeg4RotateSqueezeXYRescaledParameters
}  // namespace mmlens
