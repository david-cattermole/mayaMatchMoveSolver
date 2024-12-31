#pragma once
#include "mmlens/_cxx.h"
#include "mmlens/_symbol_export.h"
#include "mmlens/distortion_process.h"
#include <array>
#include <cstddef>
#include <cstdint>
#include <new>
#include <string>
#include <type_traits>
#include <utility>

namespace rust {
inline namespace cxxbridge1 {
// #include "rust/cxx.h"

struct unsafe_bitcopy_t;

namespace {
template <typename T>
class impl;
} // namespace

#ifndef CXXBRIDGE1_RUST_STRING
#define CXXBRIDGE1_RUST_STRING
class String final {
public:
  String() noexcept;
  String(const String &) noexcept;
  String(String &&) noexcept;
  ~String() noexcept;

  String(const std::string &);
  String(const char *);
  String(const char *, std::size_t);
  String(const char16_t *);
  String(const char16_t *, std::size_t);

  static String lossy(const std::string &) noexcept;
  static String lossy(const char *) noexcept;
  static String lossy(const char *, std::size_t) noexcept;
  static String lossy(const char16_t *) noexcept;
  static String lossy(const char16_t *, std::size_t) noexcept;

  String &operator=(const String &) &noexcept;
  String &operator=(String &&) &noexcept;

  explicit operator std::string() const;

  const char *data() const noexcept;
  std::size_t size() const noexcept;
  std::size_t length() const noexcept;
  bool empty() const noexcept;

  const char *c_str() noexcept;

  std::size_t capacity() const noexcept;
  void reserve(size_t new_cap) noexcept;

  using iterator = char *;
  iterator begin() noexcept;
  iterator end() noexcept;

  using const_iterator = const char *;
  const_iterator begin() const noexcept;
  const_iterator end() const noexcept;
  const_iterator cbegin() const noexcept;
  const_iterator cend() const noexcept;

  bool operator==(const String &) const noexcept;
  bool operator!=(const String &) const noexcept;
  bool operator<(const String &) const noexcept;
  bool operator<=(const String &) const noexcept;
  bool operator>(const String &) const noexcept;
  bool operator>=(const String &) const noexcept;

  void swap(String &) noexcept;

  String(unsafe_bitcopy_t, const String &) noexcept;

private:
  struct lossy_t;
  String(lossy_t, const char *, std::size_t) noexcept;
  String(lossy_t, const char16_t *, std::size_t) noexcept;
  friend void swap(String &lhs, String &rhs) noexcept { lhs.swap(rhs); }

  std::array<std::uintptr_t, 3> repr;
};
#endif // CXXBRIDGE1_RUST_STRING

#ifndef CXXBRIDGE1_RUST_STR
#define CXXBRIDGE1_RUST_STR
class Str final {
public:
  Str() noexcept;
  Str(const String &) noexcept;
  Str(const std::string &);
  Str(const char *);
  Str(const char *, std::size_t);

  Str &operator=(const Str &) &noexcept = default;

  explicit operator std::string() const;

  const char *data() const noexcept;
  std::size_t size() const noexcept;
  std::size_t length() const noexcept;
  bool empty() const noexcept;

  Str(const Str &) noexcept = default;
  ~Str() noexcept = default;

  using iterator = const char *;
  using const_iterator = const char *;
  const_iterator begin() const noexcept;
  const_iterator end() const noexcept;
  const_iterator cbegin() const noexcept;
  const_iterator cend() const noexcept;

  bool operator==(const Str &) const noexcept;
  bool operator!=(const Str &) const noexcept;
  bool operator<(const Str &) const noexcept;
  bool operator<=(const Str &) const noexcept;
  bool operator>(const Str &) const noexcept;
  bool operator>=(const Str &) const noexcept;

  void swap(Str &) noexcept;

private:
  class uninit;
  Str(uninit) noexcept;
  friend impl<Str>;

  std::array<std::uintptr_t, 2> repr;
};
#endif // CXXBRIDGE1_RUST_STR

#ifndef CXXBRIDGE1_RUST_BOX
#define CXXBRIDGE1_RUST_BOX
template <typename T>
class Box final {
public:
  using element_type = T;
  using const_pointer =
      typename std::add_pointer<typename std::add_const<T>::type>::type;
  using pointer = typename std::add_pointer<T>::type;

  Box() = delete;
  Box(Box &&) noexcept;
  ~Box() noexcept;

  explicit Box(const T &);
  explicit Box(T &&);

  Box &operator=(Box &&) &noexcept;

  const T *operator->() const noexcept;
  const T &operator*() const noexcept;
  T *operator->() noexcept;
  T &operator*() noexcept;

  template <typename... Fields>
  static Box in_place(Fields &&...);

  void swap(Box &) noexcept;

  static Box from_raw(T *) noexcept;

  T *into_raw() noexcept;

  /* Deprecated */ using value_type = element_type;

private:
  class uninit;
  class allocation;
  Box(uninit) noexcept;
  void drop() noexcept;

  friend void swap(Box &lhs, Box &rhs) noexcept { lhs.swap(rhs); }

  T *ptr;
};

template <typename T>
class Box<T>::uninit {};

template <typename T>
class Box<T>::allocation {
  static T *alloc() noexcept;
  static void dealloc(T *) noexcept;

public:
  allocation() noexcept : ptr(alloc()) {}
  ~allocation() noexcept {
    if (this->ptr) {
      dealloc(this->ptr);
    }
  }
  T *ptr;
};

template <typename T>
Box<T>::Box(Box &&other) noexcept : ptr(other.ptr) {
  other.ptr = nullptr;
}

template <typename T>
Box<T>::Box(const T &val) {
  allocation alloc;
  ::new (alloc.ptr) T(val);
  this->ptr = alloc.ptr;
  alloc.ptr = nullptr;
}

template <typename T>
Box<T>::Box(T &&val) {
  allocation alloc;
  ::new (alloc.ptr) T(std::move(val));
  this->ptr = alloc.ptr;
  alloc.ptr = nullptr;
}

template <typename T>
Box<T>::~Box() noexcept {
  if (this->ptr) {
    this->drop();
  }
}

template <typename T>
Box<T> &Box<T>::operator=(Box &&other) &noexcept {
  if (this->ptr) {
    this->drop();
  }
  this->ptr = other.ptr;
  other.ptr = nullptr;
  return *this;
}

template <typename T>
const T *Box<T>::operator->() const noexcept {
  return this->ptr;
}

template <typename T>
const T &Box<T>::operator*() const noexcept {
  return *this->ptr;
}

template <typename T>
T *Box<T>::operator->() noexcept {
  return this->ptr;
}

template <typename T>
T &Box<T>::operator*() noexcept {
  return *this->ptr;
}

template <typename T>
template <typename... Fields>
Box<T> Box<T>::in_place(Fields &&...fields) {
  allocation alloc;
  auto ptr = alloc.ptr;
  ::new (ptr) T{std::forward<Fields>(fields)...};
  alloc.ptr = nullptr;
  return from_raw(ptr);
}

template <typename T>
void Box<T>::swap(Box &rhs) noexcept {
  using std::swap;
  swap(this->ptr, rhs.ptr);
}

template <typename T>
Box<T> Box<T>::from_raw(T *raw) noexcept {
  Box box = uninit{};
  box.ptr = raw;
  return box;
}

template <typename T>
T *Box<T>::into_raw() noexcept {
  T *raw = this->ptr;
  this->ptr = nullptr;
  return raw;
}

template <typename T>
Box<T>::Box(uninit) noexcept {}
#endif // CXXBRIDGE1_RUST_BOX

#ifndef CXXBRIDGE1_RUST_OPAQUE
#define CXXBRIDGE1_RUST_OPAQUE
class Opaque {
public:
  Opaque() = delete;
  Opaque(const Opaque &) = delete;
  ~Opaque() = delete;
};
#endif // CXXBRIDGE1_RUST_OPAQUE

#ifndef CXXBRIDGE1_IS_COMPLETE
#define CXXBRIDGE1_IS_COMPLETE
namespace detail {
namespace {
template <typename T, typename = std::size_t>
struct is_complete : std::false_type {};
template <typename T>
struct is_complete<T, decltype(sizeof(T))> : std::true_type {};
} // namespace
} // namespace detail
#endif // CXXBRIDGE1_IS_COMPLETE

#ifndef CXXBRIDGE1_LAYOUT
#define CXXBRIDGE1_LAYOUT
class layout {
  template <typename T>
  friend std::size_t size_of();
  template <typename T>
  friend std::size_t align_of();
  template <typename T>
  static typename std::enable_if<std::is_base_of<Opaque, T>::value,
                                 std::size_t>::type
  do_size_of() {
    return T::layout::size();
  }
  template <typename T>
  static typename std::enable_if<!std::is_base_of<Opaque, T>::value,
                                 std::size_t>::type
  do_size_of() {
    return sizeof(T);
  }
  template <typename T>
  static
      typename std::enable_if<detail::is_complete<T>::value, std::size_t>::type
      size_of() {
    return do_size_of<T>();
  }
  template <typename T>
  static typename std::enable_if<std::is_base_of<Opaque, T>::value,
                                 std::size_t>::type
  do_align_of() {
    return T::layout::align();
  }
  template <typename T>
  static typename std::enable_if<!std::is_base_of<Opaque, T>::value,
                                 std::size_t>::type
  do_align_of() {
    return alignof(T);
  }
  template <typename T>
  static
      typename std::enable_if<detail::is_complete<T>::value, std::size_t>::type
      align_of() {
    return do_align_of<T>();
  }
};

template <typename T>
std::size_t size_of() {
  return layout::size_of<T>();
}

template <typename T>
std::size_t align_of() {
  return layout::align_of<T>();
}
#endif // CXXBRIDGE1_LAYOUT
} // namespace cxxbridge1
} // namespace rust

namespace mmlens {
  enum class DistortionDirection : ::std::uint8_t;
  enum class LensModelState : ::std::uint8_t;
  enum class LensModelType : ::std::uint8_t;
  struct ImageDimensions;
  struct CameraParameters;
  struct Parameters3deClassic;
  struct Parameters3deRadialStdDeg4;
  struct Parameters3deAnamorphicStdDeg4;
  struct Parameters3deAnamorphicStdDeg4Rescaled;
  struct Parameters3deAnamorphicStdDeg6;
  struct Parameters3deAnamorphicStdDeg6Rescaled;
  struct OptionParameters3deClassic;
  struct OptionParameters3deRadialStdDeg4;
  struct OptionParameters3deAnamorphicStdDeg4;
  struct OptionParameters3deAnamorphicStdDeg4Rescaled;
  struct OptionParameters3deAnamorphicStdDeg6;
  struct OptionParameters3deAnamorphicStdDeg6Rescaled;
  struct ShimDistortionLayers;
}

namespace mmlens {
#ifndef CXXBRIDGE1_ENUM_mmlens$DistortionDirection
#define CXXBRIDGE1_ENUM_mmlens$DistortionDirection
enum class DistortionDirection : ::std::uint8_t {
  kUndistort = 0,
  kRedistort = 1,
  kUndistortAndRedistort = 2,
  kRedistortAndUndistort = 3,
  kNumDistortionDirection = 4,
};
#endif // CXXBRIDGE1_ENUM_mmlens$DistortionDirection

#ifndef CXXBRIDGE1_ENUM_mmlens$LensModelState
#define CXXBRIDGE1_ENUM_mmlens$LensModelState
enum class LensModelState : ::std::uint8_t {
  kUninitialized = 0,
  kClean = 1,
  kDirty = 2,
  kNumLensModelState = 3,
};
#endif // CXXBRIDGE1_ENUM_mmlens$LensModelState

#ifndef CXXBRIDGE1_ENUM_mmlens$LensModelType
#define CXXBRIDGE1_ENUM_mmlens$LensModelType
enum class LensModelType : ::std::uint8_t {
  kUninitialized = 0,
  kPassthrough = 1,
  k3deClassic = 2,
  k3deRadialStdDeg4 = 3,
  k3deAnamorphicStdDeg4 = 4,
  k3deAnamorphicStdDeg4Rescaled = 5,
  k3deAnamorphicStdDeg6 = 6,
  k3deAnamorphicStdDeg6Rescaled = 7,
  kNumLensModelType = 8,
};
#endif // CXXBRIDGE1_ENUM_mmlens$LensModelType

#ifndef CXXBRIDGE1_STRUCT_mmlens$ImageDimensions
#define CXXBRIDGE1_STRUCT_mmlens$ImageDimensions
struct ImageDimensions final {
  ::std::size_t width;
  ::std::size_t height;
  ::std::size_t start_width;
  ::std::size_t start_height;
  ::std::size_t end_width;
  ::std::size_t end_height;

  bool operator==(const ImageDimensions &) const noexcept;
  bool operator!=(const ImageDimensions &) const noexcept;
  bool operator<(const ImageDimensions &) const noexcept;
  bool operator<=(const ImageDimensions &) const noexcept;
  bool operator>(const ImageDimensions &) const noexcept;
  bool operator>=(const ImageDimensions &) const noexcept;
  using IsRelocatable = ::std::true_type;
};
#endif // CXXBRIDGE1_STRUCT_mmlens$ImageDimensions

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
#endif // CXXBRIDGE1_STRUCT_mmlens$CameraParameters

#ifndef CXXBRIDGE1_STRUCT_mmlens$Parameters3deClassic
#define CXXBRIDGE1_STRUCT_mmlens$Parameters3deClassic
struct Parameters3deClassic final {
  double distortion;
  double anamorphic_squeeze;
  double curvature_x;
  double curvature_y;
  double quartic_distortion;

  bool operator==(const Parameters3deClassic &) const noexcept;
  bool operator!=(const Parameters3deClassic &) const noexcept;
  bool operator<(const Parameters3deClassic &) const noexcept;
  bool operator<=(const Parameters3deClassic &) const noexcept;
  bool operator>(const Parameters3deClassic &) const noexcept;
  bool operator>=(const Parameters3deClassic &) const noexcept;
  using IsRelocatable = ::std::true_type;
};
#endif // CXXBRIDGE1_STRUCT_mmlens$Parameters3deClassic

#ifndef CXXBRIDGE1_STRUCT_mmlens$Parameters3deRadialStdDeg4
#define CXXBRIDGE1_STRUCT_mmlens$Parameters3deRadialStdDeg4
struct Parameters3deRadialStdDeg4 final {
  double degree2_distortion;
  double degree2_u;
  double degree2_v;
  double degree4_distortion;
  double degree4_u;
  double degree4_v;
  double cylindric_direction;
  double cylindric_bending;

  bool operator==(const Parameters3deRadialStdDeg4 &) const noexcept;
  bool operator!=(const Parameters3deRadialStdDeg4 &) const noexcept;
  bool operator<(const Parameters3deRadialStdDeg4 &) const noexcept;
  bool operator<=(const Parameters3deRadialStdDeg4 &) const noexcept;
  bool operator>(const Parameters3deRadialStdDeg4 &) const noexcept;
  bool operator>=(const Parameters3deRadialStdDeg4 &) const noexcept;
  using IsRelocatable = ::std::true_type;
};
#endif // CXXBRIDGE1_STRUCT_mmlens$Parameters3deRadialStdDeg4

#ifndef CXXBRIDGE1_STRUCT_mmlens$Parameters3deAnamorphicStdDeg4
#define CXXBRIDGE1_STRUCT_mmlens$Parameters3deAnamorphicStdDeg4
struct Parameters3deAnamorphicStdDeg4 final {
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

  bool operator==(const Parameters3deAnamorphicStdDeg4 &) const noexcept;
  bool operator!=(const Parameters3deAnamorphicStdDeg4 &) const noexcept;
  bool operator<(const Parameters3deAnamorphicStdDeg4 &) const noexcept;
  bool operator<=(const Parameters3deAnamorphicStdDeg4 &) const noexcept;
  bool operator>(const Parameters3deAnamorphicStdDeg4 &) const noexcept;
  bool operator>=(const Parameters3deAnamorphicStdDeg4 &) const noexcept;
  using IsRelocatable = ::std::true_type;
};
#endif // CXXBRIDGE1_STRUCT_mmlens$Parameters3deAnamorphicStdDeg4

#ifndef CXXBRIDGE1_STRUCT_mmlens$Parameters3deAnamorphicStdDeg4Rescaled
#define CXXBRIDGE1_STRUCT_mmlens$Parameters3deAnamorphicStdDeg4Rescaled
struct Parameters3deAnamorphicStdDeg4Rescaled final {
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

  bool operator==(const Parameters3deAnamorphicStdDeg4Rescaled &) const noexcept;
  bool operator!=(const Parameters3deAnamorphicStdDeg4Rescaled &) const noexcept;
  bool operator<(const Parameters3deAnamorphicStdDeg4Rescaled &) const noexcept;
  bool operator<=(const Parameters3deAnamorphicStdDeg4Rescaled &) const noexcept;
  bool operator>(const Parameters3deAnamorphicStdDeg4Rescaled &) const noexcept;
  bool operator>=(const Parameters3deAnamorphicStdDeg4Rescaled &) const noexcept;
  using IsRelocatable = ::std::true_type;
};
#endif // CXXBRIDGE1_STRUCT_mmlens$Parameters3deAnamorphicStdDeg4Rescaled

#ifndef CXXBRIDGE1_STRUCT_mmlens$Parameters3deAnamorphicStdDeg6
#define CXXBRIDGE1_STRUCT_mmlens$Parameters3deAnamorphicStdDeg6
struct Parameters3deAnamorphicStdDeg6 final {
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
  double degree6_cx06;
  double degree6_cy06;
  double degree6_cx26;
  double degree6_cy26;
  double degree6_cx46;
  double degree6_cy46;
  double degree6_cx66;
  double degree6_cy66;
  double lens_rotation;
  double squeeze_x;
  double squeeze_y;

  bool operator==(const Parameters3deAnamorphicStdDeg6 &) const noexcept;
  bool operator!=(const Parameters3deAnamorphicStdDeg6 &) const noexcept;
  bool operator<(const Parameters3deAnamorphicStdDeg6 &) const noexcept;
  bool operator<=(const Parameters3deAnamorphicStdDeg6 &) const noexcept;
  bool operator>(const Parameters3deAnamorphicStdDeg6 &) const noexcept;
  bool operator>=(const Parameters3deAnamorphicStdDeg6 &) const noexcept;
  using IsRelocatable = ::std::true_type;
};
#endif // CXXBRIDGE1_STRUCT_mmlens$Parameters3deAnamorphicStdDeg6

#ifndef CXXBRIDGE1_STRUCT_mmlens$Parameters3deAnamorphicStdDeg6Rescaled
#define CXXBRIDGE1_STRUCT_mmlens$Parameters3deAnamorphicStdDeg6Rescaled
struct Parameters3deAnamorphicStdDeg6Rescaled final {
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
  double degree6_cx06;
  double degree6_cy06;
  double degree6_cx26;
  double degree6_cy26;
  double degree6_cx46;
  double degree6_cy46;
  double degree6_cx66;
  double degree6_cy66;
  double lens_rotation;
  double squeeze_x;
  double squeeze_y;
  double rescale;

  bool operator==(const Parameters3deAnamorphicStdDeg6Rescaled &) const noexcept;
  bool operator!=(const Parameters3deAnamorphicStdDeg6Rescaled &) const noexcept;
  bool operator<(const Parameters3deAnamorphicStdDeg6Rescaled &) const noexcept;
  bool operator<=(const Parameters3deAnamorphicStdDeg6Rescaled &) const noexcept;
  bool operator>(const Parameters3deAnamorphicStdDeg6Rescaled &) const noexcept;
  bool operator>=(const Parameters3deAnamorphicStdDeg6Rescaled &) const noexcept;
  using IsRelocatable = ::std::true_type;
};
#endif // CXXBRIDGE1_STRUCT_mmlens$Parameters3deAnamorphicStdDeg6Rescaled

#ifndef CXXBRIDGE1_STRUCT_mmlens$OptionParameters3deClassic
#define CXXBRIDGE1_STRUCT_mmlens$OptionParameters3deClassic
struct OptionParameters3deClassic final {
  bool exists;
  ::mmlens::Parameters3deClassic value;

  bool operator==(const OptionParameters3deClassic &) const noexcept;
  bool operator!=(const OptionParameters3deClassic &) const noexcept;
  bool operator<(const OptionParameters3deClassic &) const noexcept;
  bool operator<=(const OptionParameters3deClassic &) const noexcept;
  bool operator>(const OptionParameters3deClassic &) const noexcept;
  bool operator>=(const OptionParameters3deClassic &) const noexcept;
  using IsRelocatable = ::std::true_type;
};
#endif // CXXBRIDGE1_STRUCT_mmlens$OptionParameters3deClassic

#ifndef CXXBRIDGE1_STRUCT_mmlens$OptionParameters3deRadialStdDeg4
#define CXXBRIDGE1_STRUCT_mmlens$OptionParameters3deRadialStdDeg4
struct OptionParameters3deRadialStdDeg4 final {
  bool exists;
  ::mmlens::Parameters3deRadialStdDeg4 value;

  bool operator==(const OptionParameters3deRadialStdDeg4 &) const noexcept;
  bool operator!=(const OptionParameters3deRadialStdDeg4 &) const noexcept;
  bool operator<(const OptionParameters3deRadialStdDeg4 &) const noexcept;
  bool operator<=(const OptionParameters3deRadialStdDeg4 &) const noexcept;
  bool operator>(const OptionParameters3deRadialStdDeg4 &) const noexcept;
  bool operator>=(const OptionParameters3deRadialStdDeg4 &) const noexcept;
  using IsRelocatable = ::std::true_type;
};
#endif // CXXBRIDGE1_STRUCT_mmlens$OptionParameters3deRadialStdDeg4

#ifndef CXXBRIDGE1_STRUCT_mmlens$OptionParameters3deAnamorphicStdDeg4
#define CXXBRIDGE1_STRUCT_mmlens$OptionParameters3deAnamorphicStdDeg4
struct OptionParameters3deAnamorphicStdDeg4 final {
  bool exists;
  ::mmlens::Parameters3deAnamorphicStdDeg4 value;

  bool operator==(const OptionParameters3deAnamorphicStdDeg4 &) const noexcept;
  bool operator!=(const OptionParameters3deAnamorphicStdDeg4 &) const noexcept;
  bool operator<(const OptionParameters3deAnamorphicStdDeg4 &) const noexcept;
  bool operator<=(const OptionParameters3deAnamorphicStdDeg4 &) const noexcept;
  bool operator>(const OptionParameters3deAnamorphicStdDeg4 &) const noexcept;
  bool operator>=(const OptionParameters3deAnamorphicStdDeg4 &) const noexcept;
  using IsRelocatable = ::std::true_type;
};
#endif // CXXBRIDGE1_STRUCT_mmlens$OptionParameters3deAnamorphicStdDeg4

#ifndef CXXBRIDGE1_STRUCT_mmlens$OptionParameters3deAnamorphicStdDeg4Rescaled
#define CXXBRIDGE1_STRUCT_mmlens$OptionParameters3deAnamorphicStdDeg4Rescaled
struct OptionParameters3deAnamorphicStdDeg4Rescaled final {
  bool exists;
  ::mmlens::Parameters3deAnamorphicStdDeg4Rescaled value;

  bool operator==(const OptionParameters3deAnamorphicStdDeg4Rescaled &) const noexcept;
  bool operator!=(const OptionParameters3deAnamorphicStdDeg4Rescaled &) const noexcept;
  bool operator<(const OptionParameters3deAnamorphicStdDeg4Rescaled &) const noexcept;
  bool operator<=(const OptionParameters3deAnamorphicStdDeg4Rescaled &) const noexcept;
  bool operator>(const OptionParameters3deAnamorphicStdDeg4Rescaled &) const noexcept;
  bool operator>=(const OptionParameters3deAnamorphicStdDeg4Rescaled &) const noexcept;
  using IsRelocatable = ::std::true_type;
};
#endif // CXXBRIDGE1_STRUCT_mmlens$OptionParameters3deAnamorphicStdDeg4Rescaled

#ifndef CXXBRIDGE1_STRUCT_mmlens$OptionParameters3deAnamorphicStdDeg6
#define CXXBRIDGE1_STRUCT_mmlens$OptionParameters3deAnamorphicStdDeg6
struct OptionParameters3deAnamorphicStdDeg6 final {
  bool exists;
  ::mmlens::Parameters3deAnamorphicStdDeg6 value;

  bool operator==(const OptionParameters3deAnamorphicStdDeg6 &) const noexcept;
  bool operator!=(const OptionParameters3deAnamorphicStdDeg6 &) const noexcept;
  bool operator<(const OptionParameters3deAnamorphicStdDeg6 &) const noexcept;
  bool operator<=(const OptionParameters3deAnamorphicStdDeg6 &) const noexcept;
  bool operator>(const OptionParameters3deAnamorphicStdDeg6 &) const noexcept;
  bool operator>=(const OptionParameters3deAnamorphicStdDeg6 &) const noexcept;
  using IsRelocatable = ::std::true_type;
};
#endif // CXXBRIDGE1_STRUCT_mmlens$OptionParameters3deAnamorphicStdDeg6

#ifndef CXXBRIDGE1_STRUCT_mmlens$OptionParameters3deAnamorphicStdDeg6Rescaled
#define CXXBRIDGE1_STRUCT_mmlens$OptionParameters3deAnamorphicStdDeg6Rescaled
struct OptionParameters3deAnamorphicStdDeg6Rescaled final {
  bool exists;
  ::mmlens::Parameters3deAnamorphicStdDeg6Rescaled value;

  bool operator==(const OptionParameters3deAnamorphicStdDeg6Rescaled &) const noexcept;
  bool operator!=(const OptionParameters3deAnamorphicStdDeg6Rescaled &) const noexcept;
  bool operator<(const OptionParameters3deAnamorphicStdDeg6Rescaled &) const noexcept;
  bool operator<=(const OptionParameters3deAnamorphicStdDeg6Rescaled &) const noexcept;
  bool operator>(const OptionParameters3deAnamorphicStdDeg6Rescaled &) const noexcept;
  bool operator>=(const OptionParameters3deAnamorphicStdDeg6Rescaled &) const noexcept;
  using IsRelocatable = ::std::true_type;
};
#endif // CXXBRIDGE1_STRUCT_mmlens$OptionParameters3deAnamorphicStdDeg6Rescaled

#ifndef CXXBRIDGE1_STRUCT_mmlens$ShimDistortionLayers
#define CXXBRIDGE1_STRUCT_mmlens$ShimDistortionLayers
struct ShimDistortionLayers final : public ::rust::Opaque {
  MMLENS_API_EXPORT bool is_static() const noexcept;
  MMLENS_API_EXPORT void frame_range(::std::uint16_t &out_start_frame, ::std::uint16_t &out_end_frame) const noexcept;
  MMLENS_API_EXPORT ::std::uint16_t frame_count() const noexcept;
  MMLENS_API_EXPORT ::std::uint64_t frame_hash(::std::uint16_t frame) const noexcept;
  MMLENS_API_EXPORT ::mmlens::CameraParameters camera_parameters() const noexcept;
  MMLENS_API_EXPORT ::std::uint8_t layer_count() const noexcept;
  MMLENS_API_EXPORT ::mmlens::LensModelType layer_lens_model_type(::std::uint8_t layer_num) const noexcept;
  MMLENS_API_EXPORT ::mmlens::OptionParameters3deClassic layer_lens_parameters_3de_classic(::std::uint8_t layer_num, ::std::uint16_t frame) const noexcept;
  MMLENS_API_EXPORT ::mmlens::OptionParameters3deRadialStdDeg4 layer_lens_parameters_3de_radial_std_deg4(::std::uint8_t layer_num, ::std::uint16_t frame) const noexcept;
  MMLENS_API_EXPORT ::mmlens::OptionParameters3deAnamorphicStdDeg4 layer_lens_parameters_3de_anamorphic_std_deg4(::std::uint8_t layer_num, ::std::uint16_t frame) const noexcept;
  MMLENS_API_EXPORT ::mmlens::OptionParameters3deAnamorphicStdDeg4Rescaled layer_lens_parameters_3de_anamorphic_std_deg4_rescaled(::std::uint8_t layer_num, ::std::uint16_t frame) const noexcept;
  MMLENS_API_EXPORT ::mmlens::OptionParameters3deAnamorphicStdDeg6 layer_lens_parameters_3de_anamorphic_std_deg6(::std::uint8_t layer_num, ::std::uint16_t frame) const noexcept;
  MMLENS_API_EXPORT ::mmlens::OptionParameters3deAnamorphicStdDeg6Rescaled layer_lens_parameters_3de_anamorphic_std_deg6_rescaled(::std::uint8_t layer_num, ::std::uint16_t frame) const noexcept;
  MMLENS_API_EXPORT ::rust::String as_string() const noexcept;
  ~ShimDistortionLayers() = delete;

private:
  friend ::rust::layout;
  struct layout {
    static ::std::size_t size() noexcept;
    static ::std::size_t align() noexcept;
  };
};
#endif // CXXBRIDGE1_STRUCT_mmlens$ShimDistortionLayers

MMLENS_API_EXPORT ::rust::Box<::mmlens::ShimDistortionLayers> shim_create_distortion_layers_box() noexcept;

MMLENS_API_EXPORT ::rust::Box<::mmlens::ShimDistortionLayers> shim_read_lens_file(::rust::Str file_path) noexcept;

MMLENS_API_EXPORT ::std::int32_t initialize_global_thread_pool(::std::int32_t num_threads) noexcept;

MMLENS_API_EXPORT void apply_identity_to_f64_multithread(::mmlens::DistortionDirection direction, ::std::size_t image_width, ::std::size_t image_height, double *out_data_ptr, ::std::size_t out_data_size, ::std::size_t out_data_stride, ::mmlens::CameraParameters camera_parameters, double film_back_radius_cm, ::mmlens::Parameters3deClassic lens_parameters) noexcept;

MMLENS_API_EXPORT void apply_identity_to_f32_multithread(::mmlens::DistortionDirection direction, ::std::size_t image_width, ::std::size_t image_height, float *out_data_ptr, ::std::size_t out_data_size, ::std::size_t out_data_stride, ::mmlens::CameraParameters camera_parameters, double film_back_radius_cm, ::mmlens::Parameters3deClassic lens_parameters) noexcept;

MMLENS_API_EXPORT void apply_f64_to_f64_multithread(::mmlens::DistortionDirection direction, const double *in_data_ptr, ::std::size_t in_data_size, ::std::size_t in_data_stride, double *out_data_ptr, ::std::size_t out_data_size, ::std::size_t out_data_stride, ::mmlens::CameraParameters camera_parameters, double film_back_radius_cm, ::mmlens::Parameters3deClassic lens_parameters) noexcept;

MMLENS_API_EXPORT void apply_f64_to_f32_multithread(::mmlens::DistortionDirection direction, const double *in_data_ptr, ::std::size_t in_data_size, ::std::size_t in_data_stride, float *out_data_ptr, ::std::size_t out_data_size, ::std::size_t out_data_stride, ::mmlens::CameraParameters camera_parameters, double film_back_radius_cm, ::mmlens::Parameters3deClassic lens_parameters) noexcept;

MMLENS_API_EXPORT void apply_identity_to_f64_multithread(::mmlens::DistortionDirection direction, ::std::size_t image_width, ::std::size_t image_height, double *out_data_ptr, ::std::size_t out_data_size, ::std::size_t out_data_stride, ::mmlens::CameraParameters camera_parameters, double film_back_radius_cm, ::mmlens::Parameters3deRadialStdDeg4 lens_parameters) noexcept;

MMLENS_API_EXPORT void apply_identity_to_f32_multithread(::mmlens::DistortionDirection direction, ::std::size_t image_width, ::std::size_t image_height, float *out_data_ptr, ::std::size_t out_data_size, ::std::size_t out_data_stride, ::mmlens::CameraParameters camera_parameters, double film_back_radius_cm, ::mmlens::Parameters3deRadialStdDeg4 lens_parameters) noexcept;

MMLENS_API_EXPORT void apply_f64_to_f64_multithread(::mmlens::DistortionDirection direction, const double *in_data_ptr, ::std::size_t in_data_size, ::std::size_t in_data_stride, double *out_data_ptr, ::std::size_t out_data_size, ::std::size_t out_data_stride, ::mmlens::CameraParameters camera_parameters, double film_back_radius_cm, ::mmlens::Parameters3deRadialStdDeg4 lens_parameters) noexcept;

MMLENS_API_EXPORT void apply_f64_to_f32_multithread(::mmlens::DistortionDirection direction, const double *in_data_ptr, ::std::size_t in_data_size, ::std::size_t in_data_stride, float *out_data_ptr, ::std::size_t out_data_size, ::std::size_t out_data_stride, ::mmlens::CameraParameters camera_parameters, double film_back_radius_cm, ::mmlens::Parameters3deRadialStdDeg4 lens_parameters) noexcept;

MMLENS_API_EXPORT void apply_identity_to_f64_multithread(::mmlens::DistortionDirection direction, ::std::size_t image_width, ::std::size_t image_height, double *out_data_ptr, ::std::size_t out_data_size, ::std::size_t out_data_stride, ::mmlens::CameraParameters camera_parameters, double film_back_radius_cm, ::mmlens::Parameters3deAnamorphicStdDeg4 lens_parameters) noexcept;

MMLENS_API_EXPORT void apply_identity_to_f32_multithread(::mmlens::DistortionDirection direction, ::std::size_t image_width, ::std::size_t image_height, float *out_data_ptr, ::std::size_t out_data_size, ::std::size_t out_data_stride, ::mmlens::CameraParameters camera_parameters, double film_back_radius_cm, ::mmlens::Parameters3deAnamorphicStdDeg4 lens_parameters) noexcept;

MMLENS_API_EXPORT void apply_f64_to_f64_multithread(::mmlens::DistortionDirection direction, const double *in_data_ptr, ::std::size_t in_data_size, ::std::size_t in_data_stride, double *out_data_ptr, ::std::size_t out_data_size, ::std::size_t out_data_stride, ::mmlens::CameraParameters camera_parameters, double film_back_radius_cm, ::mmlens::Parameters3deAnamorphicStdDeg4 lens_parameters) noexcept;

MMLENS_API_EXPORT void apply_f64_to_f32_multithread(::mmlens::DistortionDirection direction, const double *in_data_ptr, ::std::size_t in_data_size, ::std::size_t in_data_stride, float *out_data_ptr, ::std::size_t out_data_size, ::std::size_t out_data_stride, ::mmlens::CameraParameters camera_parameters, double film_back_radius_cm, ::mmlens::Parameters3deAnamorphicStdDeg4 lens_parameters) noexcept;

MMLENS_API_EXPORT void apply_identity_to_f64_multithread(::mmlens::DistortionDirection direction, ::std::size_t image_width, ::std::size_t image_height, double *out_data_ptr, ::std::size_t out_data_size, ::std::size_t out_data_stride, ::mmlens::CameraParameters camera_parameters, double film_back_radius_cm, ::mmlens::Parameters3deAnamorphicStdDeg4Rescaled lens_parameters) noexcept;

MMLENS_API_EXPORT void apply_identity_to_f32_multithread(::mmlens::DistortionDirection direction, ::std::size_t image_width, ::std::size_t image_height, float *out_data_ptr, ::std::size_t out_data_size, ::std::size_t out_data_stride, ::mmlens::CameraParameters camera_parameters, double film_back_radius_cm, ::mmlens::Parameters3deAnamorphicStdDeg4Rescaled lens_parameters) noexcept;

MMLENS_API_EXPORT void apply_f64_to_f64_multithread(::mmlens::DistortionDirection direction, const double *in_data_ptr, ::std::size_t in_data_size, ::std::size_t in_data_stride, double *out_data_ptr, ::std::size_t out_data_size, ::std::size_t out_data_stride, ::mmlens::CameraParameters camera_parameters, double film_back_radius_cm, ::mmlens::Parameters3deAnamorphicStdDeg4Rescaled lens_parameters) noexcept;

MMLENS_API_EXPORT void apply_f64_to_f32_multithread(::mmlens::DistortionDirection direction, const double *in_data_ptr, ::std::size_t in_data_size, ::std::size_t in_data_stride, float *out_data_ptr, ::std::size_t out_data_size, ::std::size_t out_data_stride, ::mmlens::CameraParameters camera_parameters, double film_back_radius_cm, ::mmlens::Parameters3deAnamorphicStdDeg4Rescaled lens_parameters) noexcept;

MMLENS_API_EXPORT void apply_identity_to_f64_multithread(::mmlens::DistortionDirection direction, ::std::size_t image_width, ::std::size_t image_height, double *out_data_ptr, ::std::size_t out_data_size, ::std::size_t out_data_stride, ::mmlens::CameraParameters camera_parameters, double film_back_radius_cm, ::mmlens::Parameters3deAnamorphicStdDeg6 lens_parameters) noexcept;

MMLENS_API_EXPORT void apply_identity_to_f32_multithread(::mmlens::DistortionDirection direction, ::std::size_t image_width, ::std::size_t image_height, float *out_data_ptr, ::std::size_t out_data_size, ::std::size_t out_data_stride, ::mmlens::CameraParameters camera_parameters, double film_back_radius_cm, ::mmlens::Parameters3deAnamorphicStdDeg6 lens_parameters) noexcept;

MMLENS_API_EXPORT void apply_f64_to_f64_multithread(::mmlens::DistortionDirection direction, const double *in_data_ptr, ::std::size_t in_data_size, ::std::size_t in_data_stride, double *out_data_ptr, ::std::size_t out_data_size, ::std::size_t out_data_stride, ::mmlens::CameraParameters camera_parameters, double film_back_radius_cm, ::mmlens::Parameters3deAnamorphicStdDeg6 lens_parameters) noexcept;

MMLENS_API_EXPORT void apply_f64_to_f32_multithread(::mmlens::DistortionDirection direction, const double *in_data_ptr, ::std::size_t in_data_size, ::std::size_t in_data_stride, float *out_data_ptr, ::std::size_t out_data_size, ::std::size_t out_data_stride, ::mmlens::CameraParameters camera_parameters, double film_back_radius_cm, ::mmlens::Parameters3deAnamorphicStdDeg6 lens_parameters) noexcept;

MMLENS_API_EXPORT void apply_identity_to_f64_multithread(::mmlens::DistortionDirection direction, ::std::size_t image_width, ::std::size_t image_height, double *out_data_ptr, ::std::size_t out_data_size, ::std::size_t out_data_stride, ::mmlens::CameraParameters camera_parameters, double film_back_radius_cm, ::mmlens::Parameters3deAnamorphicStdDeg6Rescaled lens_parameters) noexcept;

MMLENS_API_EXPORT void apply_identity_to_f32_multithread(::mmlens::DistortionDirection direction, ::std::size_t image_width, ::std::size_t image_height, float *out_data_ptr, ::std::size_t out_data_size, ::std::size_t out_data_stride, ::mmlens::CameraParameters camera_parameters, double film_back_radius_cm, ::mmlens::Parameters3deAnamorphicStdDeg6Rescaled lens_parameters) noexcept;

MMLENS_API_EXPORT void apply_f64_to_f64_multithread(::mmlens::DistortionDirection direction, const double *in_data_ptr, ::std::size_t in_data_size, ::std::size_t in_data_stride, double *out_data_ptr, ::std::size_t out_data_size, ::std::size_t out_data_stride, ::mmlens::CameraParameters camera_parameters, double film_back_radius_cm, ::mmlens::Parameters3deAnamorphicStdDeg6Rescaled lens_parameters) noexcept;

MMLENS_API_EXPORT void apply_f64_to_f32_multithread(::mmlens::DistortionDirection direction, const double *in_data_ptr, ::std::size_t in_data_size, ::std::size_t in_data_stride, float *out_data_ptr, ::std::size_t out_data_size, ::std::size_t out_data_stride, ::mmlens::CameraParameters camera_parameters, double film_back_radius_cm, ::mmlens::Parameters3deAnamorphicStdDeg6Rescaled lens_parameters) noexcept;
} // namespace mmlens
