#pragma once
#include "mmscenegraph/_cxx.h"
#include "mmscenegraph/_symbol_export.h"
#include <cstdint>
#include <type_traits>

namespace mmscenegraph {
  struct Camera;
}

namespace mmscenegraph {
#ifndef CXXBRIDGE1_STRUCT_mmscenegraph$Camera
#define CXXBRIDGE1_STRUCT_mmscenegraph$Camera
struct Camera final {
  double sensor_width_mm;
  double focal_length_mm;

  bool operator==(const Camera &) const noexcept;
  bool operator!=(const Camera &) const noexcept;
  bool operator<(const Camera &) const noexcept;
  bool operator<=(const Camera &) const noexcept;
  bool operator>(const Camera &) const noexcept;
  bool operator>=(const Camera &) const noexcept;
  using IsRelocatable = ::std::true_type;
};
#endif // CXXBRIDGE1_STRUCT_mmscenegraph$Camera

MMSCENEGRAPH_API_EXPORT void foo(::std::uint32_t number) noexcept;

MMSCENEGRAPH_API_EXPORT ::std::uint32_t foobar(::std::uint32_t number) noexcept;

MMSCENEGRAPH_API_EXPORT ::mmscenegraph::Camera make_camera(double width, double focal) noexcept;
} // namespace mmscenegraph
