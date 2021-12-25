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

extern "C" {
bool mmscenegraph$cxxbridge1$Camera$operator$eq(const Camera &, const Camera &) noexcept;
bool mmscenegraph$cxxbridge1$Camera$operator$ne(const Camera &, const Camera &) noexcept;
bool mmscenegraph$cxxbridge1$Camera$operator$lt(const Camera &, const Camera &) noexcept;
bool mmscenegraph$cxxbridge1$Camera$operator$le(const Camera &, const Camera &) noexcept;
bool mmscenegraph$cxxbridge1$Camera$operator$gt(const Camera &, const Camera &) noexcept;
bool mmscenegraph$cxxbridge1$Camera$operator$ge(const Camera &, const Camera &) noexcept;

void mmscenegraph$cxxbridge1$foo(::std::uint32_t number) noexcept;

::std::uint32_t mmscenegraph$cxxbridge1$foobar(::std::uint32_t number) noexcept;

::mmscenegraph::Camera mmscenegraph$cxxbridge1$make_camera(double width, double focal) noexcept;
} // extern "C"

bool Camera::operator==(const Camera &rhs) const noexcept {
  return mmscenegraph$cxxbridge1$Camera$operator$eq(*this, rhs);
}

bool Camera::operator!=(const Camera &rhs) const noexcept {
  return mmscenegraph$cxxbridge1$Camera$operator$ne(*this, rhs);
}

bool Camera::operator<(const Camera &rhs) const noexcept {
  return mmscenegraph$cxxbridge1$Camera$operator$lt(*this, rhs);
}

bool Camera::operator<=(const Camera &rhs) const noexcept {
  return mmscenegraph$cxxbridge1$Camera$operator$le(*this, rhs);
}

bool Camera::operator>(const Camera &rhs) const noexcept {
  return mmscenegraph$cxxbridge1$Camera$operator$gt(*this, rhs);
}

bool Camera::operator>=(const Camera &rhs) const noexcept {
  return mmscenegraph$cxxbridge1$Camera$operator$ge(*this, rhs);
}

MMSCENEGRAPH_API_EXPORT void foo(::std::uint32_t number) noexcept {
  mmscenegraph$cxxbridge1$foo(number);
}

MMSCENEGRAPH_API_EXPORT ::std::uint32_t foobar(::std::uint32_t number) noexcept {
  return mmscenegraph$cxxbridge1$foobar(number);
}

MMSCENEGRAPH_API_EXPORT ::mmscenegraph::Camera make_camera(double width, double focal) noexcept {
  return mmscenegraph$cxxbridge1$make_camera(width, focal);
}
} // namespace mmscenegraph
