#include "mmscenegraph/_cxx.h"
#include "mmscenegraph/_symbol_export.h"
#include <algorithm>
#include <array>
#include <cassert>
#include <cstddef>
#include <cstdint>
#include <functional>
#include <initializer_list>
#include <iterator>
#include <new>
#include <stdexcept>
#include <type_traits>
#include <utility>

namespace rust {
inline namespace cxxbridge1 {
// #include "rust/cxx.h"

#ifndef CXXBRIDGE1_PANIC
#define CXXBRIDGE1_PANIC
template <typename Exception>
void panic [[noreturn]] (const char *msg);
#endif // CXXBRIDGE1_PANIC

namespace {
template <typename T>
class impl;
} // namespace

template <typename T>
::std::size_t size_of();
template <typename T>
::std::size_t align_of();

#ifndef CXXBRIDGE1_RUST_SLICE
#define CXXBRIDGE1_RUST_SLICE
namespace detail {
template <bool>
struct copy_assignable_if {};

template <>
struct copy_assignable_if<false> {
  copy_assignable_if() noexcept = default;
  copy_assignable_if(const copy_assignable_if &) noexcept = default;
  copy_assignable_if &operator=(const copy_assignable_if &) &noexcept = delete;
  copy_assignable_if &operator=(copy_assignable_if &&) &noexcept = default;
};
} // namespace detail

template <typename T>
class Slice final
    : private detail::copy_assignable_if<std::is_const<T>::value> {
public:
  using value_type = T;

  Slice() noexcept;
  Slice(T *, std::size_t count) noexcept;

  template <typename C>
  explicit Slice(C& c) : Slice(c.data(), c.size()) {}

  Slice &operator=(const Slice<T> &) &noexcept = default;
  Slice &operator=(Slice<T> &&) &noexcept = default;

  T *data() const noexcept;
  std::size_t size() const noexcept;
  std::size_t length() const noexcept;
  bool empty() const noexcept;

  T &operator[](std::size_t n) const noexcept;
  T &at(std::size_t n) const;
  T &front() const noexcept;
  T &back() const noexcept;

  Slice(const Slice<T> &) noexcept = default;
  ~Slice() noexcept = default;

  class iterator;
  iterator begin() const noexcept;
  iterator end() const noexcept;

  void swap(Slice &) noexcept;

private:
  class uninit;
  Slice(uninit) noexcept;
  friend impl<Slice>;
  friend void sliceInit(void *, const void *, std::size_t) noexcept;
  friend void *slicePtr(const void *) noexcept;
  friend std::size_t sliceLen(const void *) noexcept;

  std::array<std::uintptr_t, 2> repr;
};

template <typename T>
class Slice<T>::iterator final {
public:
  using iterator_category = std::random_access_iterator_tag;
  using value_type = T;
  using difference_type = std::ptrdiff_t;
  using pointer = typename std::add_pointer<T>::type;
  using reference = typename std::add_lvalue_reference<T>::type;

  reference operator*() const noexcept;
  pointer operator->() const noexcept;
  reference operator[](difference_type) const noexcept;

  iterator &operator++() noexcept;
  iterator operator++(int) noexcept;
  iterator &operator--() noexcept;
  iterator operator--(int) noexcept;

  iterator &operator+=(difference_type) noexcept;
  iterator &operator-=(difference_type) noexcept;
  iterator operator+(difference_type) const noexcept;
  iterator operator-(difference_type) const noexcept;
  difference_type operator-(const iterator &) const noexcept;

  bool operator==(const iterator &) const noexcept;
  bool operator!=(const iterator &) const noexcept;
  bool operator<(const iterator &) const noexcept;
  bool operator<=(const iterator &) const noexcept;
  bool operator>(const iterator &) const noexcept;
  bool operator>=(const iterator &) const noexcept;

private:
  friend class Slice;
  void *pos;
  std::size_t stride;
};

template <typename T>
Slice<T>::Slice() noexcept {
  sliceInit(this, reinterpret_cast<void *>(align_of<T>()), 0);
}

template <typename T>
Slice<T>::Slice(T *s, std::size_t count) noexcept {
  assert(s != nullptr || count == 0);
  sliceInit(this,
            s == nullptr && count == 0
                ? reinterpret_cast<void *>(align_of<T>())
                : const_cast<typename std::remove_const<T>::type *>(s),
            count);
}

template <typename T>
T *Slice<T>::data() const noexcept {
  return reinterpret_cast<T *>(slicePtr(this));
}

template <typename T>
std::size_t Slice<T>::size() const noexcept {
  return sliceLen(this);
}

template <typename T>
std::size_t Slice<T>::length() const noexcept {
  return this->size();
}

template <typename T>
bool Slice<T>::empty() const noexcept {
  return this->size() == 0;
}

template <typename T>
T &Slice<T>::operator[](std::size_t n) const noexcept {
  assert(n < this->size());
  auto ptr = static_cast<char *>(slicePtr(this)) + size_of<T>() * n;
  return *reinterpret_cast<T *>(ptr);
}

template <typename T>
T &Slice<T>::at(std::size_t n) const {
  if (n >= this->size()) {
    panic<std::out_of_range>("rust::Slice index out of range");
  }
  return (*this)[n];
}

template <typename T>
T &Slice<T>::front() const noexcept {
  assert(!this->empty());
  return (*this)[0];
}

template <typename T>
T &Slice<T>::back() const noexcept {
  assert(!this->empty());
  return (*this)[this->size() - 1];
}

template <typename T>
typename Slice<T>::iterator::reference
Slice<T>::iterator::operator*() const noexcept {
  return *static_cast<T *>(this->pos);
}

template <typename T>
typename Slice<T>::iterator::pointer
Slice<T>::iterator::operator->() const noexcept {
  return static_cast<T *>(this->pos);
}

template <typename T>
typename Slice<T>::iterator::reference Slice<T>::iterator::operator[](
    typename Slice<T>::iterator::difference_type n) const noexcept {
  auto ptr = static_cast<char *>(this->pos) + this->stride * n;
  return *reinterpret_cast<T *>(ptr);
}

template <typename T>
typename Slice<T>::iterator &Slice<T>::iterator::operator++() noexcept {
  this->pos = static_cast<char *>(this->pos) + this->stride;
  return *this;
}

template <typename T>
typename Slice<T>::iterator Slice<T>::iterator::operator++(int) noexcept {
  auto ret = iterator(*this);
  this->pos = static_cast<char *>(this->pos) + this->stride;
  return ret;
}

template <typename T>
typename Slice<T>::iterator &Slice<T>::iterator::operator--() noexcept {
  this->pos = static_cast<char *>(this->pos) - this->stride;
  return *this;
}

template <typename T>
typename Slice<T>::iterator Slice<T>::iterator::operator--(int) noexcept {
  auto ret = iterator(*this);
  this->pos = static_cast<char *>(this->pos) - this->stride;
  return ret;
}

template <typename T>
typename Slice<T>::iterator &Slice<T>::iterator::operator+=(
    typename Slice<T>::iterator::difference_type n) noexcept {
  this->pos = static_cast<char *>(this->pos) + this->stride * n;
  return *this;
}

template <typename T>
typename Slice<T>::iterator &Slice<T>::iterator::operator-=(
    typename Slice<T>::iterator::difference_type n) noexcept {
  this->pos = static_cast<char *>(this->pos) - this->stride * n;
  return *this;
}

template <typename T>
typename Slice<T>::iterator Slice<T>::iterator::operator+(
    typename Slice<T>::iterator::difference_type n) const noexcept {
  auto ret = iterator(*this);
  ret.pos = static_cast<char *>(this->pos) + this->stride * n;
  return ret;
}

template <typename T>
typename Slice<T>::iterator Slice<T>::iterator::operator-(
    typename Slice<T>::iterator::difference_type n) const noexcept {
  auto ret = iterator(*this);
  ret.pos = static_cast<char *>(this->pos) - this->stride * n;
  return ret;
}

template <typename T>
typename Slice<T>::iterator::difference_type
Slice<T>::iterator::operator-(const iterator &other) const noexcept {
  auto diff = std::distance(static_cast<char *>(other.pos),
                            static_cast<char *>(this->pos));
  return diff / static_cast<typename Slice<T>::iterator::difference_type>(
                    this->stride);
}

template <typename T>
bool Slice<T>::iterator::operator==(const iterator &other) const noexcept {
  return this->pos == other.pos;
}

template <typename T>
bool Slice<T>::iterator::operator!=(const iterator &other) const noexcept {
  return this->pos != other.pos;
}

template <typename T>
bool Slice<T>::iterator::operator<(const iterator &other) const noexcept {
  return this->pos < other.pos;
}

template <typename T>
bool Slice<T>::iterator::operator<=(const iterator &other) const noexcept {
  return this->pos <= other.pos;
}

template <typename T>
bool Slice<T>::iterator::operator>(const iterator &other) const noexcept {
  return this->pos > other.pos;
}

template <typename T>
bool Slice<T>::iterator::operator>=(const iterator &other) const noexcept {
  return this->pos >= other.pos;
}

template <typename T>
typename Slice<T>::iterator Slice<T>::begin() const noexcept {
  iterator it;
  it.pos = slicePtr(this);
  it.stride = size_of<T>();
  return it;
}

template <typename T>
typename Slice<T>::iterator Slice<T>::end() const noexcept {
  iterator it = this->begin();
  it.pos = static_cast<char *>(it.pos) + it.stride * this->size();
  return it;
}

template <typename T>
void Slice<T>::swap(Slice &rhs) noexcept {
  std::swap(*this, rhs);
}
#endif // CXXBRIDGE1_RUST_SLICE

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

#ifndef CXXBRIDGE1_RUST_BITCOPY_T
#define CXXBRIDGE1_RUST_BITCOPY_T
struct unsafe_bitcopy_t final {
  explicit unsafe_bitcopy_t() = default;
};
#endif // CXXBRIDGE1_RUST_BITCOPY_T

#ifndef CXXBRIDGE1_RUST_VEC
#define CXXBRIDGE1_RUST_VEC
template <typename T>
class Vec final {
public:
  using value_type = T;

  Vec() noexcept;
  Vec(std::initializer_list<T>);
  Vec(const Vec &);
  Vec(Vec &&) noexcept;
  ~Vec() noexcept;

  Vec &operator=(Vec &&) &noexcept;
  Vec &operator=(const Vec &) &;

  std::size_t size() const noexcept;
  bool empty() const noexcept;
  const T *data() const noexcept;
  T *data() noexcept;
  std::size_t capacity() const noexcept;

  const T &operator[](std::size_t n) const noexcept;
  const T &at(std::size_t n) const;
  const T &front() const noexcept;
  const T &back() const noexcept;

  T &operator[](std::size_t n) noexcept;
  T &at(std::size_t n);
  T &front() noexcept;
  T &back() noexcept;

  void reserve(std::size_t new_cap);
  void push_back(const T &value);
  void push_back(T &&value);
  template <typename... Args>
  void emplace_back(Args &&...args);
  void truncate(std::size_t len);
  void clear();

  using iterator = typename Slice<T>::iterator;
  iterator begin() noexcept;
  iterator end() noexcept;

  using const_iterator = typename Slice<const T>::iterator;
  const_iterator begin() const noexcept;
  const_iterator end() const noexcept;
  const_iterator cbegin() const noexcept;
  const_iterator cend() const noexcept;

  void swap(Vec &) noexcept;

  Vec(unsafe_bitcopy_t, const Vec &) noexcept;

private:
  void reserve_total(std::size_t new_cap) noexcept;
  void set_len(std::size_t len) noexcept;
  void drop() noexcept;

  friend void swap(Vec &lhs, Vec &rhs) noexcept { lhs.swap(rhs); }

  std::array<std::uintptr_t, 3> repr;
};

template <typename T>
Vec<T>::Vec(std::initializer_list<T> init) : Vec{} {
  this->reserve_total(init.size());
  std::move(init.begin(), init.end(), std::back_inserter(*this));
}

template <typename T>
Vec<T>::Vec(const Vec &other) : Vec() {
  this->reserve_total(other.size());
  std::copy(other.begin(), other.end(), std::back_inserter(*this));
}

template <typename T>
Vec<T>::Vec(Vec &&other) noexcept : repr(other.repr) {
  new (&other) Vec();
}

template <typename T>
Vec<T>::~Vec() noexcept {
  this->drop();
}

template <typename T>
Vec<T> &Vec<T>::operator=(Vec &&other) &noexcept {
  this->drop();
  this->repr = other.repr;
  new (&other) Vec();
  return *this;
}

template <typename T>
Vec<T> &Vec<T>::operator=(const Vec &other) & {
  if (this != &other) {
    this->drop();
    new (this) Vec(other);
  }
  return *this;
}

template <typename T>
bool Vec<T>::empty() const noexcept {
  return this->size() == 0;
}

template <typename T>
T *Vec<T>::data() noexcept {
  return const_cast<T *>(const_cast<const Vec<T> *>(this)->data());
}

template <typename T>
const T &Vec<T>::operator[](std::size_t n) const noexcept {
  assert(n < this->size());
  auto data = reinterpret_cast<const char *>(this->data());
  return *reinterpret_cast<const T *>(data + n * size_of<T>());
}

template <typename T>
const T &Vec<T>::at(std::size_t n) const {
  if (n >= this->size()) {
    panic<std::out_of_range>("rust::Vec index out of range");
  }
  return (*this)[n];
}

template <typename T>
const T &Vec<T>::front() const noexcept {
  assert(!this->empty());
  return (*this)[0];
}

template <typename T>
const T &Vec<T>::back() const noexcept {
  assert(!this->empty());
  return (*this)[this->size() - 1];
}

template <typename T>
T &Vec<T>::operator[](std::size_t n) noexcept {
  assert(n < this->size());
  auto data = reinterpret_cast<char *>(this->data());
  return *reinterpret_cast<T *>(data + n * size_of<T>());
}

template <typename T>
T &Vec<T>::at(std::size_t n) {
  if (n >= this->size()) {
    panic<std::out_of_range>("rust::Vec index out of range");
  }
  return (*this)[n];
}

template <typename T>
T &Vec<T>::front() noexcept {
  assert(!this->empty());
  return (*this)[0];
}

template <typename T>
T &Vec<T>::back() noexcept {
  assert(!this->empty());
  return (*this)[this->size() - 1];
}

template <typename T>
void Vec<T>::reserve(std::size_t new_cap) {
  this->reserve_total(new_cap);
}

template <typename T>
void Vec<T>::push_back(const T &value) {
  this->emplace_back(value);
}

template <typename T>
void Vec<T>::push_back(T &&value) {
  this->emplace_back(std::move(value));
}

template <typename T>
template <typename... Args>
void Vec<T>::emplace_back(Args &&...args) {
  auto size = this->size();
  this->reserve_total(size + 1);
  ::new (reinterpret_cast<T *>(reinterpret_cast<char *>(this->data()) +
                               size * size_of<T>()))
      T(std::forward<Args>(args)...);
  this->set_len(size + 1);
}

template <typename T>
void Vec<T>::clear() {
  this->truncate(0);
}

template <typename T>
typename Vec<T>::iterator Vec<T>::begin() noexcept {
  return Slice<T>(this->data(), this->size()).begin();
}

template <typename T>
typename Vec<T>::iterator Vec<T>::end() noexcept {
  return Slice<T>(this->data(), this->size()).end();
}

template <typename T>
typename Vec<T>::const_iterator Vec<T>::begin() const noexcept {
  return this->cbegin();
}

template <typename T>
typename Vec<T>::const_iterator Vec<T>::end() const noexcept {
  return this->cend();
}

template <typename T>
typename Vec<T>::const_iterator Vec<T>::cbegin() const noexcept {
  return Slice<const T>(this->data(), this->size()).begin();
}

template <typename T>
typename Vec<T>::const_iterator Vec<T>::cend() const noexcept {
  return Slice<const T>(this->data(), this->size()).end();
}

template <typename T>
void Vec<T>::swap(Vec &rhs) noexcept {
  using std::swap;
  swap(this->repr, rhs.repr);
}

template <typename T>
Vec<T>::Vec(unsafe_bitcopy_t, const Vec &bits) noexcept : repr(bits.repr) {}
#endif // CXXBRIDGE1_RUST_VEC

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

template <typename T>
class Slice<T>::uninit {};
template <typename T>
inline Slice<T>::Slice(uninit) noexcept {}

namespace repr {
using Fat = ::std::array<::std::uintptr_t, 2>;
} // namespace repr

template <typename T>
union ManuallyDrop {
  T value;
  ManuallyDrop(T &&value) : value(::std::move(value)) {}
  ~ManuallyDrop() {}
};

namespace {
template <typename T>
class impl<Slice<T>> final {
public:
  static Slice<T> slice(repr::Fat repr) noexcept {
    Slice<T> slice = typename Slice<T>::uninit{};
    slice.repr = repr;
    return slice;
  }
};
} // namespace
} // namespace cxxbridge1
} // namespace rust

namespace mmscenegraph {
  enum class NodeType : ::std::uint8_t;
  struct Point3;
  struct NodeId;
  enum class AttrType : ::std::uint8_t;
  struct AttrId;
  struct Translate2DAttrIds;
  struct Translate3DAttrIds;
  struct Rotate3DAttrIds;
  struct Scale3DAttrIds;
  struct CameraAttrIds;
  struct MarkerAttrIds;
  enum class RotateOrder : ::std::uint8_t;
  enum class FilmFit : ::std::uint8_t;
  struct TransformNode;
  struct BundleNode;
  struct CameraNode;
  struct MarkerNode;
  struct ShimAttrDataBlock;
  struct ShimSceneGraph;
  struct ShimFlatScene;
  struct ShimEvaluationObjects;
  enum class ControlPointDistribution : ::std::uint8_t;
  enum class Interpolation : ::std::uint8_t;
}

namespace mmscenegraph {
#ifndef CXXBRIDGE1_ENUM_mmscenegraph$NodeType
#define CXXBRIDGE1_ENUM_mmscenegraph$NodeType
enum class NodeType : ::std::uint8_t {
  kTransform = 0,
  kBundle = 1,
  kMarker = 2,
  kCamera = 3,
  kRoot = 4,
  kNone = 5,
  kUnknown = 255,
};
#endif // CXXBRIDGE1_ENUM_mmscenegraph$NodeType

#ifndef CXXBRIDGE1_STRUCT_mmscenegraph$Point3
#define CXXBRIDGE1_STRUCT_mmscenegraph$Point3
struct Point3 final {
  double x;
  double y;
  double z;

  bool operator==(Point3 const &) const noexcept;
  bool operator!=(Point3 const &) const noexcept;
  using IsRelocatable = ::std::true_type;
};
#endif // CXXBRIDGE1_STRUCT_mmscenegraph$Point3

#ifndef CXXBRIDGE1_STRUCT_mmscenegraph$NodeId
#define CXXBRIDGE1_STRUCT_mmscenegraph$NodeId
struct NodeId final {
  ::mmscenegraph::NodeType node_type;
  ::std::size_t index;

  bool operator==(NodeId const &) const noexcept;
  bool operator!=(NodeId const &) const noexcept;
  bool operator<(NodeId const &) const noexcept;
  bool operator<=(NodeId const &) const noexcept;
  bool operator>(NodeId const &) const noexcept;
  bool operator>=(NodeId const &) const noexcept;
  using IsRelocatable = ::std::true_type;
};
#endif // CXXBRIDGE1_STRUCT_mmscenegraph$NodeId

#ifndef CXXBRIDGE1_ENUM_mmscenegraph$AttrType
#define CXXBRIDGE1_ENUM_mmscenegraph$AttrType
enum class AttrType : ::std::uint8_t {
  kAnimDense = 0,
  kStatic = 1,
  kNone = 2,
  kUnknown = 255,
};
#endif // CXXBRIDGE1_ENUM_mmscenegraph$AttrType

#ifndef CXXBRIDGE1_STRUCT_mmscenegraph$AttrId
#define CXXBRIDGE1_STRUCT_mmscenegraph$AttrId
struct AttrId final {
  ::mmscenegraph::AttrType attr_type;
  ::std::size_t index;

  bool operator==(AttrId const &) const noexcept;
  bool operator!=(AttrId const &) const noexcept;
  bool operator<(AttrId const &) const noexcept;
  bool operator<=(AttrId const &) const noexcept;
  bool operator>(AttrId const &) const noexcept;
  bool operator>=(AttrId const &) const noexcept;
  using IsRelocatable = ::std::true_type;
};
#endif // CXXBRIDGE1_STRUCT_mmscenegraph$AttrId

#ifndef CXXBRIDGE1_STRUCT_mmscenegraph$Translate2DAttrIds
#define CXXBRIDGE1_STRUCT_mmscenegraph$Translate2DAttrIds
struct Translate2DAttrIds final {
  ::mmscenegraph::AttrId tx;
  ::mmscenegraph::AttrId ty;

  using IsRelocatable = ::std::true_type;
};
#endif // CXXBRIDGE1_STRUCT_mmscenegraph$Translate2DAttrIds

#ifndef CXXBRIDGE1_STRUCT_mmscenegraph$Translate3DAttrIds
#define CXXBRIDGE1_STRUCT_mmscenegraph$Translate3DAttrIds
struct Translate3DAttrIds final {
  ::mmscenegraph::AttrId tx;
  ::mmscenegraph::AttrId ty;
  ::mmscenegraph::AttrId tz;

  using IsRelocatable = ::std::true_type;
};
#endif // CXXBRIDGE1_STRUCT_mmscenegraph$Translate3DAttrIds

#ifndef CXXBRIDGE1_STRUCT_mmscenegraph$Rotate3DAttrIds
#define CXXBRIDGE1_STRUCT_mmscenegraph$Rotate3DAttrIds
struct Rotate3DAttrIds final {
  ::mmscenegraph::AttrId rx;
  ::mmscenegraph::AttrId ry;
  ::mmscenegraph::AttrId rz;

  using IsRelocatable = ::std::true_type;
};
#endif // CXXBRIDGE1_STRUCT_mmscenegraph$Rotate3DAttrIds

#ifndef CXXBRIDGE1_STRUCT_mmscenegraph$Scale3DAttrIds
#define CXXBRIDGE1_STRUCT_mmscenegraph$Scale3DAttrIds
struct Scale3DAttrIds final {
  ::mmscenegraph::AttrId sx;
  ::mmscenegraph::AttrId sy;
  ::mmscenegraph::AttrId sz;

  using IsRelocatable = ::std::true_type;
};
#endif // CXXBRIDGE1_STRUCT_mmscenegraph$Scale3DAttrIds

#ifndef CXXBRIDGE1_STRUCT_mmscenegraph$CameraAttrIds
#define CXXBRIDGE1_STRUCT_mmscenegraph$CameraAttrIds
struct CameraAttrIds final {
  ::mmscenegraph::AttrId sensor_width;
  ::mmscenegraph::AttrId sensor_height;
  ::mmscenegraph::AttrId focal_length;
  ::mmscenegraph::AttrId lens_offset_x;
  ::mmscenegraph::AttrId lens_offset_y;
  ::mmscenegraph::AttrId near_clip_plane;
  ::mmscenegraph::AttrId far_clip_plane;
  ::mmscenegraph::AttrId camera_scale;

  using IsRelocatable = ::std::true_type;
};
#endif // CXXBRIDGE1_STRUCT_mmscenegraph$CameraAttrIds

#ifndef CXXBRIDGE1_STRUCT_mmscenegraph$MarkerAttrIds
#define CXXBRIDGE1_STRUCT_mmscenegraph$MarkerAttrIds
struct MarkerAttrIds final {
  ::mmscenegraph::AttrId tx;
  ::mmscenegraph::AttrId ty;
  ::mmscenegraph::AttrId weight;

  using IsRelocatable = ::std::true_type;
};
#endif // CXXBRIDGE1_STRUCT_mmscenegraph$MarkerAttrIds

#ifndef CXXBRIDGE1_ENUM_mmscenegraph$RotateOrder
#define CXXBRIDGE1_ENUM_mmscenegraph$RotateOrder
enum class RotateOrder : ::std::uint8_t {
  kXYZ = 0,
  kYXZ = 4,
  kZXY = 2,
  kXZY = 3,
  kZYX = 5,
  kYZX = 1,
  kUnknown = 255,
};
#endif // CXXBRIDGE1_ENUM_mmscenegraph$RotateOrder

#ifndef CXXBRIDGE1_ENUM_mmscenegraph$FilmFit
#define CXXBRIDGE1_ENUM_mmscenegraph$FilmFit
enum class FilmFit : ::std::uint8_t {
  kFill = 0,
  kHorizontal = 1,
  kVertical = 2,
  kOverscan = 3,
  kUnknown = 255,
};
#endif // CXXBRIDGE1_ENUM_mmscenegraph$FilmFit

#ifndef CXXBRIDGE1_STRUCT_mmscenegraph$TransformNode
#define CXXBRIDGE1_STRUCT_mmscenegraph$TransformNode
struct TransformNode final {
  ::mmscenegraph::NodeId id;
  ::mmscenegraph::AttrId attr_tx;
  ::mmscenegraph::AttrId attr_ty;
  ::mmscenegraph::AttrId attr_tz;
  ::mmscenegraph::AttrId attr_rx;
  ::mmscenegraph::AttrId attr_ry;
  ::mmscenegraph::AttrId attr_rz;
  ::mmscenegraph::AttrId attr_sx;
  ::mmscenegraph::AttrId attr_sy;
  ::mmscenegraph::AttrId attr_sz;
  ::mmscenegraph::RotateOrder rotate_order;

  bool operator==(TransformNode const &) const noexcept;
  bool operator!=(TransformNode const &) const noexcept;
  bool operator<(TransformNode const &) const noexcept;
  bool operator<=(TransformNode const &) const noexcept;
  bool operator>(TransformNode const &) const noexcept;
  bool operator>=(TransformNode const &) const noexcept;
  using IsRelocatable = ::std::true_type;
};
#endif // CXXBRIDGE1_STRUCT_mmscenegraph$TransformNode

#ifndef CXXBRIDGE1_STRUCT_mmscenegraph$BundleNode
#define CXXBRIDGE1_STRUCT_mmscenegraph$BundleNode
struct BundleNode final {
  ::mmscenegraph::NodeId id;
  ::mmscenegraph::AttrId attr_tx;
  ::mmscenegraph::AttrId attr_ty;
  ::mmscenegraph::AttrId attr_tz;
  ::mmscenegraph::AttrId attr_rx;
  ::mmscenegraph::AttrId attr_ry;
  ::mmscenegraph::AttrId attr_rz;
  ::mmscenegraph::AttrId attr_sx;
  ::mmscenegraph::AttrId attr_sy;
  ::mmscenegraph::AttrId attr_sz;
  ::mmscenegraph::RotateOrder rotate_order;

  bool operator==(BundleNode const &) const noexcept;
  bool operator!=(BundleNode const &) const noexcept;
  bool operator<(BundleNode const &) const noexcept;
  bool operator<=(BundleNode const &) const noexcept;
  bool operator>(BundleNode const &) const noexcept;
  bool operator>=(BundleNode const &) const noexcept;
  using IsRelocatable = ::std::true_type;
};
#endif // CXXBRIDGE1_STRUCT_mmscenegraph$BundleNode

#ifndef CXXBRIDGE1_STRUCT_mmscenegraph$CameraNode
#define CXXBRIDGE1_STRUCT_mmscenegraph$CameraNode
struct CameraNode final {
  ::mmscenegraph::NodeId id;
  ::mmscenegraph::AttrId attr_tx;
  ::mmscenegraph::AttrId attr_ty;
  ::mmscenegraph::AttrId attr_tz;
  ::mmscenegraph::AttrId attr_rx;
  ::mmscenegraph::AttrId attr_ry;
  ::mmscenegraph::AttrId attr_rz;
  ::mmscenegraph::AttrId attr_sx;
  ::mmscenegraph::AttrId attr_sy;
  ::mmscenegraph::AttrId attr_sz;
  ::mmscenegraph::RotateOrder rotate_order;
  ::mmscenegraph::AttrId attr_sensor_width;
  ::mmscenegraph::AttrId attr_sensor_height;
  ::mmscenegraph::AttrId attr_focal_length;
  ::mmscenegraph::AttrId attr_lens_offset_x;
  ::mmscenegraph::AttrId attr_lens_offset_y;
  ::mmscenegraph::AttrId attr_near_clip_plane;
  ::mmscenegraph::AttrId attr_far_clip_plane;
  ::mmscenegraph::AttrId attr_camera_scale;
  ::mmscenegraph::FilmFit film_fit;
  ::std::int32_t render_image_width;
  ::std::int32_t render_image_height;

  bool operator==(CameraNode const &) const noexcept;
  bool operator!=(CameraNode const &) const noexcept;
  bool operator<(CameraNode const &) const noexcept;
  bool operator<=(CameraNode const &) const noexcept;
  bool operator>(CameraNode const &) const noexcept;
  bool operator>=(CameraNode const &) const noexcept;
  using IsRelocatable = ::std::true_type;
};
#endif // CXXBRIDGE1_STRUCT_mmscenegraph$CameraNode

#ifndef CXXBRIDGE1_STRUCT_mmscenegraph$MarkerNode
#define CXXBRIDGE1_STRUCT_mmscenegraph$MarkerNode
struct MarkerNode final {
  ::mmscenegraph::NodeId id;
  ::mmscenegraph::AttrId attr_tx;
  ::mmscenegraph::AttrId attr_ty;
  ::mmscenegraph::AttrId attr_weight;

  bool operator==(MarkerNode const &) const noexcept;
  bool operator!=(MarkerNode const &) const noexcept;
  bool operator<(MarkerNode const &) const noexcept;
  bool operator<=(MarkerNode const &) const noexcept;
  bool operator>(MarkerNode const &) const noexcept;
  bool operator>=(MarkerNode const &) const noexcept;
  using IsRelocatable = ::std::true_type;
};
#endif // CXXBRIDGE1_STRUCT_mmscenegraph$MarkerNode

#ifndef CXXBRIDGE1_STRUCT_mmscenegraph$ShimAttrDataBlock
#define CXXBRIDGE1_STRUCT_mmscenegraph$ShimAttrDataBlock
struct ShimAttrDataBlock final : public ::rust::Opaque {
  MMSCENEGRAPH_API_EXPORT void clear() noexcept;
  MMSCENEGRAPH_API_EXPORT ::std::size_t num_attr_static() const noexcept;
  MMSCENEGRAPH_API_EXPORT ::std::size_t num_attr_anim_dense() const noexcept;
  MMSCENEGRAPH_API_EXPORT ::mmscenegraph::AttrId create_attr_static(double value) noexcept;
  MMSCENEGRAPH_API_EXPORT ::mmscenegraph::AttrId create_attr_anim_dense(::rust::Vec<double> values, ::std::uint32_t frame_start) noexcept;
  MMSCENEGRAPH_API_EXPORT double get_attr_value(::mmscenegraph::AttrId attr_id, ::std::uint32_t frame) const noexcept;
  MMSCENEGRAPH_API_EXPORT bool set_attr_value(::mmscenegraph::AttrId attr_id, ::std::uint32_t frame, double value) noexcept;
  ~ShimAttrDataBlock() = delete;

private:
  friend ::rust::layout;
  struct layout {
    static ::std::size_t size() noexcept;
    static ::std::size_t align() noexcept;
  };
};
#endif // CXXBRIDGE1_STRUCT_mmscenegraph$ShimAttrDataBlock

#ifndef CXXBRIDGE1_STRUCT_mmscenegraph$ShimSceneGraph
#define CXXBRIDGE1_STRUCT_mmscenegraph$ShimSceneGraph
struct ShimSceneGraph final : public ::rust::Opaque {
  MMSCENEGRAPH_API_EXPORT void clear() noexcept;
  MMSCENEGRAPH_API_EXPORT ::std::size_t num_transform_nodes() const noexcept;
  MMSCENEGRAPH_API_EXPORT ::std::size_t num_bundle_nodes() const noexcept;
  MMSCENEGRAPH_API_EXPORT ::std::size_t num_camera_nodes() const noexcept;
  MMSCENEGRAPH_API_EXPORT ::std::size_t num_marker_nodes() const noexcept;
  MMSCENEGRAPH_API_EXPORT ::mmscenegraph::TransformNode create_transform_node(::mmscenegraph::Translate3DAttrIds translate_attrs, ::mmscenegraph::Rotate3DAttrIds rotate_attrs, ::mmscenegraph::Scale3DAttrIds scale_attrs, ::mmscenegraph::RotateOrder rotate_order) noexcept;
  MMSCENEGRAPH_API_EXPORT ::mmscenegraph::BundleNode create_bundle_node(::mmscenegraph::Translate3DAttrIds translate_attrs, ::mmscenegraph::Rotate3DAttrIds rotate_attrs, ::mmscenegraph::Scale3DAttrIds scale_attrs, ::mmscenegraph::RotateOrder rotate_order) noexcept;
  MMSCENEGRAPH_API_EXPORT ::mmscenegraph::CameraNode create_camera_node(::mmscenegraph::Translate3DAttrIds translate_attrs, ::mmscenegraph::Rotate3DAttrIds rotate_attrs, ::mmscenegraph::Scale3DAttrIds scale_attrs, ::mmscenegraph::CameraAttrIds camera_attrs, ::mmscenegraph::RotateOrder rotate_order, ::mmscenegraph::FilmFit film_fit, ::std::int32_t render_image_width, ::std::int32_t render_image_height) noexcept;
  MMSCENEGRAPH_API_EXPORT ::mmscenegraph::MarkerNode create_marker_node(::mmscenegraph::MarkerAttrIds marker_attrs) noexcept;
  MMSCENEGRAPH_API_EXPORT bool link_marker_to_camera(::mmscenegraph::NodeId mkr_node_id, ::mmscenegraph::NodeId cam_node_id) noexcept;
  MMSCENEGRAPH_API_EXPORT bool link_marker_to_bundle(::mmscenegraph::NodeId mkr_node_id, ::mmscenegraph::NodeId bnd_node_id) noexcept;
  MMSCENEGRAPH_API_EXPORT bool set_node_parent(::mmscenegraph::NodeId child_node_id, ::mmscenegraph::NodeId parent_node_id) noexcept;
  ~ShimSceneGraph() = delete;

private:
  friend ::rust::layout;
  struct layout {
    static ::std::size_t size() noexcept;
    static ::std::size_t align() noexcept;
  };
};
#endif // CXXBRIDGE1_STRUCT_mmscenegraph$ShimSceneGraph

#ifndef CXXBRIDGE1_STRUCT_mmscenegraph$ShimFlatScene
#define CXXBRIDGE1_STRUCT_mmscenegraph$ShimFlatScene
struct ShimFlatScene final : public ::rust::Opaque {
  MMSCENEGRAPH_API_EXPORT ::rust::Slice<double const> markers() const noexcept;
  MMSCENEGRAPH_API_EXPORT ::rust::Slice<double const> points() const noexcept;
  MMSCENEGRAPH_API_EXPORT ::std::size_t num_markers() const noexcept;
  MMSCENEGRAPH_API_EXPORT ::std::size_t num_points() const noexcept;
  MMSCENEGRAPH_API_EXPORT void evaluate(::rust::Box<::mmscenegraph::ShimAttrDataBlock> const &attrdb, ::rust::Slice<::std::uint32_t const> frame_list) noexcept;
  ~ShimFlatScene() = delete;

private:
  friend ::rust::layout;
  struct layout {
    static ::std::size_t size() noexcept;
    static ::std::size_t align() noexcept;
  };
};
#endif // CXXBRIDGE1_STRUCT_mmscenegraph$ShimFlatScene

#ifndef CXXBRIDGE1_STRUCT_mmscenegraph$ShimEvaluationObjects
#define CXXBRIDGE1_STRUCT_mmscenegraph$ShimEvaluationObjects
struct ShimEvaluationObjects final : public ::rust::Opaque {
  MMSCENEGRAPH_API_EXPORT void clear_all() noexcept;
  MMSCENEGRAPH_API_EXPORT void clear_bundles() noexcept;
  MMSCENEGRAPH_API_EXPORT void clear_markers() noexcept;
  MMSCENEGRAPH_API_EXPORT void clear_cameras() noexcept;
  MMSCENEGRAPH_API_EXPORT ::std::size_t num_bundles() const noexcept;
  MMSCENEGRAPH_API_EXPORT ::std::size_t num_markers() const noexcept;
  MMSCENEGRAPH_API_EXPORT ::std::size_t num_cameras() const noexcept;
  MMSCENEGRAPH_API_EXPORT void add_bundle(::mmscenegraph::BundleNode const &bnd_node) noexcept;
  MMSCENEGRAPH_API_EXPORT void add_camera(::mmscenegraph::CameraNode const &cam_node) noexcept;
  MMSCENEGRAPH_API_EXPORT void add_marker(::mmscenegraph::MarkerNode const &mkr_node) noexcept;
  ~ShimEvaluationObjects() = delete;

private:
  friend ::rust::layout;
  struct layout {
    static ::std::size_t size() noexcept;
    static ::std::size_t align() noexcept;
  };
};
#endif // CXXBRIDGE1_STRUCT_mmscenegraph$ShimEvaluationObjects

#ifndef CXXBRIDGE1_ENUM_mmscenegraph$ControlPointDistribution
#define CXXBRIDGE1_ENUM_mmscenegraph$ControlPointDistribution
enum class ControlPointDistribution : ::std::uint8_t {
  kUniform = 1,
  kAutoKeypoints = 2,
  kUnknown = 255,
};
#endif // CXXBRIDGE1_ENUM_mmscenegraph$ControlPointDistribution

#ifndef CXXBRIDGE1_ENUM_mmscenegraph$Interpolation
#define CXXBRIDGE1_ENUM_mmscenegraph$Interpolation
enum class Interpolation : ::std::uint8_t {
  kLinear = 1,
  kQuadraticNUBS = 2,
  kCubicNUBS = 3,
  kCubicSpline = 4,
  kUnknown = 255,
};
#endif // CXXBRIDGE1_ENUM_mmscenegraph$Interpolation

extern "C" {
bool mmscenegraph$cxxbridge1$Point3$operator$eq(Point3 const &, Point3 const &) noexcept;
bool mmscenegraph$cxxbridge1$Point3$operator$ne(Point3 const &, Point3 const &) noexcept;
bool mmscenegraph$cxxbridge1$NodeId$operator$eq(NodeId const &, NodeId const &) noexcept;
bool mmscenegraph$cxxbridge1$NodeId$operator$lt(NodeId const &, NodeId const &) noexcept;
bool mmscenegraph$cxxbridge1$NodeId$operator$le(NodeId const &, NodeId const &) noexcept;
::std::size_t mmscenegraph$cxxbridge1$NodeId$operator$hash(NodeId const &) noexcept;
bool mmscenegraph$cxxbridge1$AttrId$operator$eq(AttrId const &, AttrId const &) noexcept;
bool mmscenegraph$cxxbridge1$AttrId$operator$lt(AttrId const &, AttrId const &) noexcept;
bool mmscenegraph$cxxbridge1$AttrId$operator$le(AttrId const &, AttrId const &) noexcept;
::std::size_t mmscenegraph$cxxbridge1$AttrId$operator$hash(AttrId const &) noexcept;
::std::size_t mmscenegraph$cxxbridge1$Translate2DAttrIds$operator$hash(Translate2DAttrIds const &) noexcept;
::std::size_t mmscenegraph$cxxbridge1$Translate3DAttrIds$operator$hash(Translate3DAttrIds const &) noexcept;
::std::size_t mmscenegraph$cxxbridge1$Rotate3DAttrIds$operator$hash(Rotate3DAttrIds const &) noexcept;
::std::size_t mmscenegraph$cxxbridge1$Scale3DAttrIds$operator$hash(Scale3DAttrIds const &) noexcept;
::std::size_t mmscenegraph$cxxbridge1$CameraAttrIds$operator$hash(CameraAttrIds const &) noexcept;
::std::size_t mmscenegraph$cxxbridge1$MarkerAttrIds$operator$hash(MarkerAttrIds const &) noexcept;
bool mmscenegraph$cxxbridge1$TransformNode$operator$eq(TransformNode const &, TransformNode const &) noexcept;
bool mmscenegraph$cxxbridge1$TransformNode$operator$lt(TransformNode const &, TransformNode const &) noexcept;
bool mmscenegraph$cxxbridge1$TransformNode$operator$le(TransformNode const &, TransformNode const &) noexcept;
::std::size_t mmscenegraph$cxxbridge1$TransformNode$operator$hash(TransformNode const &) noexcept;
bool mmscenegraph$cxxbridge1$BundleNode$operator$eq(BundleNode const &, BundleNode const &) noexcept;
bool mmscenegraph$cxxbridge1$BundleNode$operator$lt(BundleNode const &, BundleNode const &) noexcept;
bool mmscenegraph$cxxbridge1$BundleNode$operator$le(BundleNode const &, BundleNode const &) noexcept;
::std::size_t mmscenegraph$cxxbridge1$BundleNode$operator$hash(BundleNode const &) noexcept;
bool mmscenegraph$cxxbridge1$CameraNode$operator$eq(CameraNode const &, CameraNode const &) noexcept;
bool mmscenegraph$cxxbridge1$CameraNode$operator$lt(CameraNode const &, CameraNode const &) noexcept;
bool mmscenegraph$cxxbridge1$CameraNode$operator$le(CameraNode const &, CameraNode const &) noexcept;
::std::size_t mmscenegraph$cxxbridge1$CameraNode$operator$hash(CameraNode const &) noexcept;
bool mmscenegraph$cxxbridge1$MarkerNode$operator$eq(MarkerNode const &, MarkerNode const &) noexcept;
bool mmscenegraph$cxxbridge1$MarkerNode$operator$lt(MarkerNode const &, MarkerNode const &) noexcept;
bool mmscenegraph$cxxbridge1$MarkerNode$operator$le(MarkerNode const &, MarkerNode const &) noexcept;
::std::size_t mmscenegraph$cxxbridge1$MarkerNode$operator$hash(MarkerNode const &) noexcept;
::std::size_t mmscenegraph$cxxbridge1$ShimAttrDataBlock$operator$sizeof() noexcept;
::std::size_t mmscenegraph$cxxbridge1$ShimAttrDataBlock$operator$alignof() noexcept;

void mmscenegraph$cxxbridge1$ShimAttrDataBlock$clear(::mmscenegraph::ShimAttrDataBlock &self) noexcept;

::std::size_t mmscenegraph$cxxbridge1$ShimAttrDataBlock$num_attr_static(::mmscenegraph::ShimAttrDataBlock const &self) noexcept;

::std::size_t mmscenegraph$cxxbridge1$ShimAttrDataBlock$num_attr_anim_dense(::mmscenegraph::ShimAttrDataBlock const &self) noexcept;

::mmscenegraph::AttrId mmscenegraph$cxxbridge1$ShimAttrDataBlock$create_attr_static(::mmscenegraph::ShimAttrDataBlock &self, double value) noexcept;

::mmscenegraph::AttrId mmscenegraph$cxxbridge1$ShimAttrDataBlock$create_attr_anim_dense(::mmscenegraph::ShimAttrDataBlock &self, ::rust::Vec<double> *values, ::std::uint32_t frame_start) noexcept;

double mmscenegraph$cxxbridge1$ShimAttrDataBlock$get_attr_value(::mmscenegraph::ShimAttrDataBlock const &self, ::mmscenegraph::AttrId attr_id, ::std::uint32_t frame) noexcept;

bool mmscenegraph$cxxbridge1$ShimAttrDataBlock$set_attr_value(::mmscenegraph::ShimAttrDataBlock &self, ::mmscenegraph::AttrId attr_id, ::std::uint32_t frame, double value) noexcept;

::mmscenegraph::ShimAttrDataBlock *mmscenegraph$cxxbridge1$shim_create_attr_data_block_box() noexcept;
::std::size_t mmscenegraph$cxxbridge1$ShimSceneGraph$operator$sizeof() noexcept;
::std::size_t mmscenegraph$cxxbridge1$ShimSceneGraph$operator$alignof() noexcept;

void mmscenegraph$cxxbridge1$ShimSceneGraph$clear(::mmscenegraph::ShimSceneGraph &self) noexcept;

::std::size_t mmscenegraph$cxxbridge1$ShimSceneGraph$num_transform_nodes(::mmscenegraph::ShimSceneGraph const &self) noexcept;

::std::size_t mmscenegraph$cxxbridge1$ShimSceneGraph$num_bundle_nodes(::mmscenegraph::ShimSceneGraph const &self) noexcept;

::std::size_t mmscenegraph$cxxbridge1$ShimSceneGraph$num_camera_nodes(::mmscenegraph::ShimSceneGraph const &self) noexcept;

::std::size_t mmscenegraph$cxxbridge1$ShimSceneGraph$num_marker_nodes(::mmscenegraph::ShimSceneGraph const &self) noexcept;

::mmscenegraph::TransformNode mmscenegraph$cxxbridge1$ShimSceneGraph$create_transform_node(::mmscenegraph::ShimSceneGraph &self, ::mmscenegraph::Translate3DAttrIds translate_attrs, ::mmscenegraph::Rotate3DAttrIds rotate_attrs, ::mmscenegraph::Scale3DAttrIds scale_attrs, ::mmscenegraph::RotateOrder rotate_order) noexcept;

::mmscenegraph::BundleNode mmscenegraph$cxxbridge1$ShimSceneGraph$create_bundle_node(::mmscenegraph::ShimSceneGraph &self, ::mmscenegraph::Translate3DAttrIds translate_attrs, ::mmscenegraph::Rotate3DAttrIds rotate_attrs, ::mmscenegraph::Scale3DAttrIds scale_attrs, ::mmscenegraph::RotateOrder rotate_order) noexcept;

::mmscenegraph::CameraNode mmscenegraph$cxxbridge1$ShimSceneGraph$create_camera_node(::mmscenegraph::ShimSceneGraph &self, ::mmscenegraph::Translate3DAttrIds translate_attrs, ::mmscenegraph::Rotate3DAttrIds rotate_attrs, ::mmscenegraph::Scale3DAttrIds scale_attrs, ::mmscenegraph::CameraAttrIds camera_attrs, ::mmscenegraph::RotateOrder rotate_order, ::mmscenegraph::FilmFit film_fit, ::std::int32_t render_image_width, ::std::int32_t render_image_height) noexcept;

::mmscenegraph::MarkerNode mmscenegraph$cxxbridge1$ShimSceneGraph$create_marker_node(::mmscenegraph::ShimSceneGraph &self, ::mmscenegraph::MarkerAttrIds marker_attrs) noexcept;

bool mmscenegraph$cxxbridge1$ShimSceneGraph$link_marker_to_camera(::mmscenegraph::ShimSceneGraph &self, ::mmscenegraph::NodeId mkr_node_id, ::mmscenegraph::NodeId cam_node_id) noexcept;

bool mmscenegraph$cxxbridge1$ShimSceneGraph$link_marker_to_bundle(::mmscenegraph::ShimSceneGraph &self, ::mmscenegraph::NodeId mkr_node_id, ::mmscenegraph::NodeId bnd_node_id) noexcept;

bool mmscenegraph$cxxbridge1$ShimSceneGraph$set_node_parent(::mmscenegraph::ShimSceneGraph &self, ::mmscenegraph::NodeId child_node_id, ::mmscenegraph::NodeId parent_node_id) noexcept;

::mmscenegraph::ShimSceneGraph *mmscenegraph$cxxbridge1$shim_create_scene_graph_box() noexcept;
::std::size_t mmscenegraph$cxxbridge1$ShimFlatScene$operator$sizeof() noexcept;
::std::size_t mmscenegraph$cxxbridge1$ShimFlatScene$operator$alignof() noexcept;

::rust::repr::Fat mmscenegraph$cxxbridge1$ShimFlatScene$markers(::mmscenegraph::ShimFlatScene const &self) noexcept;

::rust::repr::Fat mmscenegraph$cxxbridge1$ShimFlatScene$points(::mmscenegraph::ShimFlatScene const &self) noexcept;

::std::size_t mmscenegraph$cxxbridge1$ShimFlatScene$num_markers(::mmscenegraph::ShimFlatScene const &self) noexcept;

::std::size_t mmscenegraph$cxxbridge1$ShimFlatScene$num_points(::mmscenegraph::ShimFlatScene const &self) noexcept;

void mmscenegraph$cxxbridge1$ShimFlatScene$evaluate(::mmscenegraph::ShimFlatScene &self, ::rust::Box<::mmscenegraph::ShimAttrDataBlock> const &attrdb, ::rust::Slice<::std::uint32_t const> frame_list) noexcept;

::mmscenegraph::ShimFlatScene *mmscenegraph$cxxbridge1$shim_bake_scene_graph(::rust::Box<::mmscenegraph::ShimSceneGraph> const &sg, ::rust::Box<::mmscenegraph::ShimEvaluationObjects> const &eval_objects) noexcept;

::mmscenegraph::ShimFlatScene *mmscenegraph$cxxbridge1$shim_create_flat_scene_box() noexcept;
::std::size_t mmscenegraph$cxxbridge1$ShimEvaluationObjects$operator$sizeof() noexcept;
::std::size_t mmscenegraph$cxxbridge1$ShimEvaluationObjects$operator$alignof() noexcept;

void mmscenegraph$cxxbridge1$ShimEvaluationObjects$clear_all(::mmscenegraph::ShimEvaluationObjects &self) noexcept;

void mmscenegraph$cxxbridge1$ShimEvaluationObjects$clear_bundles(::mmscenegraph::ShimEvaluationObjects &self) noexcept;

void mmscenegraph$cxxbridge1$ShimEvaluationObjects$clear_markers(::mmscenegraph::ShimEvaluationObjects &self) noexcept;

void mmscenegraph$cxxbridge1$ShimEvaluationObjects$clear_cameras(::mmscenegraph::ShimEvaluationObjects &self) noexcept;

::std::size_t mmscenegraph$cxxbridge1$ShimEvaluationObjects$num_bundles(::mmscenegraph::ShimEvaluationObjects const &self) noexcept;

::std::size_t mmscenegraph$cxxbridge1$ShimEvaluationObjects$num_markers(::mmscenegraph::ShimEvaluationObjects const &self) noexcept;

::std::size_t mmscenegraph$cxxbridge1$ShimEvaluationObjects$num_cameras(::mmscenegraph::ShimEvaluationObjects const &self) noexcept;

void mmscenegraph$cxxbridge1$ShimEvaluationObjects$add_bundle(::mmscenegraph::ShimEvaluationObjects &self, ::mmscenegraph::BundleNode const &bnd_node) noexcept;

void mmscenegraph$cxxbridge1$ShimEvaluationObjects$add_camera(::mmscenegraph::ShimEvaluationObjects &self, ::mmscenegraph::CameraNode const &cam_node) noexcept;

void mmscenegraph$cxxbridge1$ShimEvaluationObjects$add_marker(::mmscenegraph::ShimEvaluationObjects &self, ::mmscenegraph::MarkerNode const &mkr_node) noexcept;

::mmscenegraph::ShimEvaluationObjects *mmscenegraph$cxxbridge1$shim_create_evaluation_objects_box() noexcept;

bool mmscenegraph$cxxbridge1$shim_fit_line_to_points_type2(::rust::Slice<double const> x, ::rust::Slice<double const> y, double &out_point_x, double &out_point_y, double &out_dir_x, double &out_dir_y) noexcept;

bool mmscenegraph$cxxbridge1$shim_fit_straight_line_to_ordered_points(::rust::Slice<double const> points_coord_x, ::rust::Slice<double const> points_coord_y, double &out_point_x, double &out_point_y, double &out_dir_x, double &out_dir_y) noexcept;

bool mmscenegraph$cxxbridge1$shim_line_point_intersection(::mmscenegraph::Point3 point, ::mmscenegraph::Point3 line_a, ::mmscenegraph::Point3 line_b, ::mmscenegraph::Point3 &out_point) noexcept;

bool mmscenegraph$cxxbridge1$shim_fit_plane_to_points(::rust::Slice<double const> points_xyz, double &out_point_x, double &out_point_y, double &out_point_z, double &out_dir_x, double &out_dir_y, double &out_dir_z, double &out_scale, double &out_rms_error) noexcept;

bool mmscenegraph$cxxbridge1$shim_detect_curve_pops(::rust::Slice<double const> x_values, ::rust::Slice<double const> y_values, double threshold, ::rust::Vec<double> &out_x_values, ::rust::Vec<double> &out_y_values) noexcept;

bool mmscenegraph$cxxbridge1$shim_filter_curve_pops(::rust::Slice<double const> x_values, ::rust::Slice<double const> y_values, double threshold, ::rust::Vec<double> &out_x_values, ::rust::Vec<double> &out_y_values) noexcept;

bool mmscenegraph$cxxbridge1$shim_curve_simplify(::rust::Slice<double const> x_values, ::rust::Slice<double const> y_values, ::std::size_t control_point_count, ::mmscenegraph::ControlPointDistribution distribution, ::mmscenegraph::Interpolation interpolation_method, ::rust::Vec<double> &out_x_values, ::rust::Vec<double> &out_y_values) noexcept;

double mmscenegraph$cxxbridge1$shim_gaussian(double x, double mean, double sigma) noexcept;

bool mmscenegraph$cxxbridge1$shim_calc_mean_absolute_deviation(::rust::Slice<double const> data, double &out_mean) noexcept;

bool mmscenegraph$cxxbridge1$shim_calc_population_variance(::rust::Slice<double const> data, double &out_mean, double &out_variance) noexcept;

bool mmscenegraph$cxxbridge1$shim_calc_sample_variance(::rust::Slice<double const> data, double &out_mean, double &out_variance) noexcept;

bool mmscenegraph$cxxbridge1$shim_calc_population_standard_deviation(::rust::Slice<double const> data, double &out_mean, double &out_std_dev) noexcept;

bool mmscenegraph$cxxbridge1$shim_calc_sample_standard_deviation(::rust::Slice<double const> data, double &out_mean, double &out_std_dev) noexcept;

bool mmscenegraph$cxxbridge1$shim_calc_population_coefficient_of_variation(::rust::Slice<double const> data, double &out_mean, double &out_cv) noexcept;

bool mmscenegraph$cxxbridge1$shim_calc_sample_coefficient_of_variation(::rust::Slice<double const> data, double &out_mean, double &out_cv) noexcept;

bool mmscenegraph$cxxbridge1$shim_calc_population_relative_standard_deviation(::rust::Slice<double const> data, double &out_mean, double &out_rsd) noexcept;

bool mmscenegraph$cxxbridge1$shim_calc_sample_relative_standard_deviation(::rust::Slice<double const> data, double &out_mean, double &out_rsd) noexcept;

double mmscenegraph$cxxbridge1$shim_calc_z_score(double mean, double std_dev, double value) noexcept;

bool mmscenegraph$cxxbridge1$shim_calc_peak_to_peak(::rust::Slice<double const> data, double &out_value) noexcept;

bool mmscenegraph$cxxbridge1$shim_calc_skewness_type1(::rust::Slice<double const> data, double &out_mean, double &out_skewness) noexcept;

bool mmscenegraph$cxxbridge1$shim_calc_skewness_type2(::rust::Slice<double const> data, double &out_mean, double &out_skewness) noexcept;

bool mmscenegraph$cxxbridge1$shim_calc_population_kurtosis_excess(::rust::Slice<double const> data, double &out_mean, double &out_kurtosis) noexcept;

bool mmscenegraph$cxxbridge1$shim_calc_sample_kurtosis_excess(::rust::Slice<double const> data, double &out_mean, double &out_kurtosis) noexcept;

bool mmscenegraph$cxxbridge1$shim_calc_local_minima_maxima(::rust::Slice<double const> data, ::rust::Vec<::std::size_t> &out_indices) noexcept;

bool mmscenegraph$cxxbridge1$shim_calc_signal_to_noise_ratio(::rust::Slice<double const> data, double &out_mean, double &out_snr) noexcept;

bool mmscenegraph$cxxbridge1$shim_calc_signal_to_noise_ratio_as_decibels(::rust::Slice<double const> data, double &out_mean, double &out_snr_db) noexcept;

bool mmscenegraph$cxxbridge1$shim_calc_median_absolute_deviation(::rust::Slice<double const> sorted_data, double &out_median, double &out_mad) noexcept;

bool mmscenegraph$cxxbridge1$shim_calc_median_absolute_deviation_sigma(double value, ::rust::Slice<double const> sorted_data, double &out_median, double &out_sigma) noexcept;

bool mmscenegraph$cxxbridge1$shim_calc_quantile(::rust::Slice<double const> sorted_data, double probability, double &out_value) noexcept;

bool mmscenegraph$cxxbridge1$shim_calc_quartiles(::rust::Slice<double const> sorted_data, double &out_q1, double &out_q2, double &out_q3) noexcept;

bool mmscenegraph$cxxbridge1$shim_calc_interquartile_range(::rust::Slice<double const> sorted_data, double &out_median, double &out_iqr) noexcept;

bool mmscenegraph$cxxbridge1$shim_calc_percentile_rank(::rust::Slice<double const> sorted_data, double value, double &out_rank) noexcept;

bool mmscenegraph$cxxbridge1$shim_calc_mean_absolute_error(::rust::Slice<double const> actual, ::rust::Slice<double const> predicted, double &out_mae) noexcept;

bool mmscenegraph$cxxbridge1$shim_calc_root_mean_square_error(::rust::Slice<double const> actual, ::rust::Slice<double const> predicted, double &out_rmse) noexcept;

bool mmscenegraph$cxxbridge1$shim_calc_normalized_root_mean_square_error(::rust::Slice<double const> actual, ::rust::Slice<double const> predicted, double &out_nrmse) noexcept;

bool mmscenegraph$cxxbridge1$shim_calc_coefficient_of_determination(::rust::Slice<double const> actual, ::rust::Slice<double const> predicted, double &out_r_squared) noexcept;
} // extern "C"
} // namespace mmscenegraph

namespace std {
template <> struct hash<::mmscenegraph::NodeId> {
  ::std::size_t operator()(::mmscenegraph::NodeId const &self) const noexcept {
    return ::mmscenegraph::mmscenegraph$cxxbridge1$NodeId$operator$hash(self);
  }
};

template <> struct hash<::mmscenegraph::AttrId> {
  ::std::size_t operator()(::mmscenegraph::AttrId const &self) const noexcept {
    return ::mmscenegraph::mmscenegraph$cxxbridge1$AttrId$operator$hash(self);
  }
};

template <> struct hash<::mmscenegraph::Translate2DAttrIds> {
  ::std::size_t operator()(::mmscenegraph::Translate2DAttrIds const &self) const noexcept {
    return ::mmscenegraph::mmscenegraph$cxxbridge1$Translate2DAttrIds$operator$hash(self);
  }
};

template <> struct hash<::mmscenegraph::Translate3DAttrIds> {
  ::std::size_t operator()(::mmscenegraph::Translate3DAttrIds const &self) const noexcept {
    return ::mmscenegraph::mmscenegraph$cxxbridge1$Translate3DAttrIds$operator$hash(self);
  }
};

template <> struct hash<::mmscenegraph::Rotate3DAttrIds> {
  ::std::size_t operator()(::mmscenegraph::Rotate3DAttrIds const &self) const noexcept {
    return ::mmscenegraph::mmscenegraph$cxxbridge1$Rotate3DAttrIds$operator$hash(self);
  }
};

template <> struct hash<::mmscenegraph::Scale3DAttrIds> {
  ::std::size_t operator()(::mmscenegraph::Scale3DAttrIds const &self) const noexcept {
    return ::mmscenegraph::mmscenegraph$cxxbridge1$Scale3DAttrIds$operator$hash(self);
  }
};

template <> struct hash<::mmscenegraph::CameraAttrIds> {
  ::std::size_t operator()(::mmscenegraph::CameraAttrIds const &self) const noexcept {
    return ::mmscenegraph::mmscenegraph$cxxbridge1$CameraAttrIds$operator$hash(self);
  }
};

template <> struct hash<::mmscenegraph::MarkerAttrIds> {
  ::std::size_t operator()(::mmscenegraph::MarkerAttrIds const &self) const noexcept {
    return ::mmscenegraph::mmscenegraph$cxxbridge1$MarkerAttrIds$operator$hash(self);
  }
};

template <> struct hash<::mmscenegraph::TransformNode> {
  ::std::size_t operator()(::mmscenegraph::TransformNode const &self) const noexcept {
    return ::mmscenegraph::mmscenegraph$cxxbridge1$TransformNode$operator$hash(self);
  }
};

template <> struct hash<::mmscenegraph::BundleNode> {
  ::std::size_t operator()(::mmscenegraph::BundleNode const &self) const noexcept {
    return ::mmscenegraph::mmscenegraph$cxxbridge1$BundleNode$operator$hash(self);
  }
};

template <> struct hash<::mmscenegraph::CameraNode> {
  ::std::size_t operator()(::mmscenegraph::CameraNode const &self) const noexcept {
    return ::mmscenegraph::mmscenegraph$cxxbridge1$CameraNode$operator$hash(self);
  }
};

template <> struct hash<::mmscenegraph::MarkerNode> {
  ::std::size_t operator()(::mmscenegraph::MarkerNode const &self) const noexcept {
    return ::mmscenegraph::mmscenegraph$cxxbridge1$MarkerNode$operator$hash(self);
  }
};
} // namespace std

namespace mmscenegraph {
bool Point3::operator==(Point3 const &rhs) const noexcept {
  return mmscenegraph$cxxbridge1$Point3$operator$eq(*this, rhs);
}

bool Point3::operator!=(Point3 const &rhs) const noexcept {
  return mmscenegraph$cxxbridge1$Point3$operator$ne(*this, rhs);
}

bool NodeId::operator==(NodeId const &rhs) const noexcept {
  return mmscenegraph$cxxbridge1$NodeId$operator$eq(*this, rhs);
}

bool NodeId::operator!=(NodeId const &rhs) const noexcept {
  return !(*this == rhs);
}

bool NodeId::operator<(NodeId const &rhs) const noexcept {
  return mmscenegraph$cxxbridge1$NodeId$operator$lt(*this, rhs);
}

bool NodeId::operator<=(NodeId const &rhs) const noexcept {
  return mmscenegraph$cxxbridge1$NodeId$operator$le(*this, rhs);
}

bool NodeId::operator>(NodeId const &rhs) const noexcept {
  return !(*this <= rhs);
}

bool NodeId::operator>=(NodeId const &rhs) const noexcept {
  return !(*this < rhs);
}

bool AttrId::operator==(AttrId const &rhs) const noexcept {
  return mmscenegraph$cxxbridge1$AttrId$operator$eq(*this, rhs);
}

bool AttrId::operator!=(AttrId const &rhs) const noexcept {
  return !(*this == rhs);
}

bool AttrId::operator<(AttrId const &rhs) const noexcept {
  return mmscenegraph$cxxbridge1$AttrId$operator$lt(*this, rhs);
}

bool AttrId::operator<=(AttrId const &rhs) const noexcept {
  return mmscenegraph$cxxbridge1$AttrId$operator$le(*this, rhs);
}

bool AttrId::operator>(AttrId const &rhs) const noexcept {
  return !(*this <= rhs);
}

bool AttrId::operator>=(AttrId const &rhs) const noexcept {
  return !(*this < rhs);
}

bool TransformNode::operator==(TransformNode const &rhs) const noexcept {
  return mmscenegraph$cxxbridge1$TransformNode$operator$eq(*this, rhs);
}

bool TransformNode::operator!=(TransformNode const &rhs) const noexcept {
  return !(*this == rhs);
}

bool TransformNode::operator<(TransformNode const &rhs) const noexcept {
  return mmscenegraph$cxxbridge1$TransformNode$operator$lt(*this, rhs);
}

bool TransformNode::operator<=(TransformNode const &rhs) const noexcept {
  return mmscenegraph$cxxbridge1$TransformNode$operator$le(*this, rhs);
}

bool TransformNode::operator>(TransformNode const &rhs) const noexcept {
  return !(*this <= rhs);
}

bool TransformNode::operator>=(TransformNode const &rhs) const noexcept {
  return !(*this < rhs);
}

bool BundleNode::operator==(BundleNode const &rhs) const noexcept {
  return mmscenegraph$cxxbridge1$BundleNode$operator$eq(*this, rhs);
}

bool BundleNode::operator!=(BundleNode const &rhs) const noexcept {
  return !(*this == rhs);
}

bool BundleNode::operator<(BundleNode const &rhs) const noexcept {
  return mmscenegraph$cxxbridge1$BundleNode$operator$lt(*this, rhs);
}

bool BundleNode::operator<=(BundleNode const &rhs) const noexcept {
  return mmscenegraph$cxxbridge1$BundleNode$operator$le(*this, rhs);
}

bool BundleNode::operator>(BundleNode const &rhs) const noexcept {
  return !(*this <= rhs);
}

bool BundleNode::operator>=(BundleNode const &rhs) const noexcept {
  return !(*this < rhs);
}

bool CameraNode::operator==(CameraNode const &rhs) const noexcept {
  return mmscenegraph$cxxbridge1$CameraNode$operator$eq(*this, rhs);
}

bool CameraNode::operator!=(CameraNode const &rhs) const noexcept {
  return !(*this == rhs);
}

bool CameraNode::operator<(CameraNode const &rhs) const noexcept {
  return mmscenegraph$cxxbridge1$CameraNode$operator$lt(*this, rhs);
}

bool CameraNode::operator<=(CameraNode const &rhs) const noexcept {
  return mmscenegraph$cxxbridge1$CameraNode$operator$le(*this, rhs);
}

bool CameraNode::operator>(CameraNode const &rhs) const noexcept {
  return !(*this <= rhs);
}

bool CameraNode::operator>=(CameraNode const &rhs) const noexcept {
  return !(*this < rhs);
}

bool MarkerNode::operator==(MarkerNode const &rhs) const noexcept {
  return mmscenegraph$cxxbridge1$MarkerNode$operator$eq(*this, rhs);
}

bool MarkerNode::operator!=(MarkerNode const &rhs) const noexcept {
  return !(*this == rhs);
}

bool MarkerNode::operator<(MarkerNode const &rhs) const noexcept {
  return mmscenegraph$cxxbridge1$MarkerNode$operator$lt(*this, rhs);
}

bool MarkerNode::operator<=(MarkerNode const &rhs) const noexcept {
  return mmscenegraph$cxxbridge1$MarkerNode$operator$le(*this, rhs);
}

bool MarkerNode::operator>(MarkerNode const &rhs) const noexcept {
  return !(*this <= rhs);
}

bool MarkerNode::operator>=(MarkerNode const &rhs) const noexcept {
  return !(*this < rhs);
}

::std::size_t ShimAttrDataBlock::layout::size() noexcept {
  return mmscenegraph$cxxbridge1$ShimAttrDataBlock$operator$sizeof();
}

::std::size_t ShimAttrDataBlock::layout::align() noexcept {
  return mmscenegraph$cxxbridge1$ShimAttrDataBlock$operator$alignof();
}

MMSCENEGRAPH_API_EXPORT void ShimAttrDataBlock::clear() noexcept {
  mmscenegraph$cxxbridge1$ShimAttrDataBlock$clear(*this);
}

MMSCENEGRAPH_API_EXPORT ::std::size_t ShimAttrDataBlock::num_attr_static() const noexcept {
  return mmscenegraph$cxxbridge1$ShimAttrDataBlock$num_attr_static(*this);
}

MMSCENEGRAPH_API_EXPORT ::std::size_t ShimAttrDataBlock::num_attr_anim_dense() const noexcept {
  return mmscenegraph$cxxbridge1$ShimAttrDataBlock$num_attr_anim_dense(*this);
}

MMSCENEGRAPH_API_EXPORT ::mmscenegraph::AttrId ShimAttrDataBlock::create_attr_static(double value) noexcept {
  return mmscenegraph$cxxbridge1$ShimAttrDataBlock$create_attr_static(*this, value);
}

MMSCENEGRAPH_API_EXPORT ::mmscenegraph::AttrId ShimAttrDataBlock::create_attr_anim_dense(::rust::Vec<double> values, ::std::uint32_t frame_start) noexcept {
  ::rust::ManuallyDrop<::rust::Vec<double>> values$(::std::move(values));
  return mmscenegraph$cxxbridge1$ShimAttrDataBlock$create_attr_anim_dense(*this, &values$.value, frame_start);
}

MMSCENEGRAPH_API_EXPORT double ShimAttrDataBlock::get_attr_value(::mmscenegraph::AttrId attr_id, ::std::uint32_t frame) const noexcept {
  return mmscenegraph$cxxbridge1$ShimAttrDataBlock$get_attr_value(*this, attr_id, frame);
}

MMSCENEGRAPH_API_EXPORT bool ShimAttrDataBlock::set_attr_value(::mmscenegraph::AttrId attr_id, ::std::uint32_t frame, double value) noexcept {
  return mmscenegraph$cxxbridge1$ShimAttrDataBlock$set_attr_value(*this, attr_id, frame, value);
}

MMSCENEGRAPH_API_EXPORT ::rust::Box<::mmscenegraph::ShimAttrDataBlock> shim_create_attr_data_block_box() noexcept {
  return ::rust::Box<::mmscenegraph::ShimAttrDataBlock>::from_raw(mmscenegraph$cxxbridge1$shim_create_attr_data_block_box());
}

::std::size_t ShimSceneGraph::layout::size() noexcept {
  return mmscenegraph$cxxbridge1$ShimSceneGraph$operator$sizeof();
}

::std::size_t ShimSceneGraph::layout::align() noexcept {
  return mmscenegraph$cxxbridge1$ShimSceneGraph$operator$alignof();
}

MMSCENEGRAPH_API_EXPORT void ShimSceneGraph::clear() noexcept {
  mmscenegraph$cxxbridge1$ShimSceneGraph$clear(*this);
}

MMSCENEGRAPH_API_EXPORT ::std::size_t ShimSceneGraph::num_transform_nodes() const noexcept {
  return mmscenegraph$cxxbridge1$ShimSceneGraph$num_transform_nodes(*this);
}

MMSCENEGRAPH_API_EXPORT ::std::size_t ShimSceneGraph::num_bundle_nodes() const noexcept {
  return mmscenegraph$cxxbridge1$ShimSceneGraph$num_bundle_nodes(*this);
}

MMSCENEGRAPH_API_EXPORT ::std::size_t ShimSceneGraph::num_camera_nodes() const noexcept {
  return mmscenegraph$cxxbridge1$ShimSceneGraph$num_camera_nodes(*this);
}

MMSCENEGRAPH_API_EXPORT ::std::size_t ShimSceneGraph::num_marker_nodes() const noexcept {
  return mmscenegraph$cxxbridge1$ShimSceneGraph$num_marker_nodes(*this);
}

MMSCENEGRAPH_API_EXPORT ::mmscenegraph::TransformNode ShimSceneGraph::create_transform_node(::mmscenegraph::Translate3DAttrIds translate_attrs, ::mmscenegraph::Rotate3DAttrIds rotate_attrs, ::mmscenegraph::Scale3DAttrIds scale_attrs, ::mmscenegraph::RotateOrder rotate_order) noexcept {
  return mmscenegraph$cxxbridge1$ShimSceneGraph$create_transform_node(*this, translate_attrs, rotate_attrs, scale_attrs, rotate_order);
}

MMSCENEGRAPH_API_EXPORT ::mmscenegraph::BundleNode ShimSceneGraph::create_bundle_node(::mmscenegraph::Translate3DAttrIds translate_attrs, ::mmscenegraph::Rotate3DAttrIds rotate_attrs, ::mmscenegraph::Scale3DAttrIds scale_attrs, ::mmscenegraph::RotateOrder rotate_order) noexcept {
  return mmscenegraph$cxxbridge1$ShimSceneGraph$create_bundle_node(*this, translate_attrs, rotate_attrs, scale_attrs, rotate_order);
}

MMSCENEGRAPH_API_EXPORT ::mmscenegraph::CameraNode ShimSceneGraph::create_camera_node(::mmscenegraph::Translate3DAttrIds translate_attrs, ::mmscenegraph::Rotate3DAttrIds rotate_attrs, ::mmscenegraph::Scale3DAttrIds scale_attrs, ::mmscenegraph::CameraAttrIds camera_attrs, ::mmscenegraph::RotateOrder rotate_order, ::mmscenegraph::FilmFit film_fit, ::std::int32_t render_image_width, ::std::int32_t render_image_height) noexcept {
  return mmscenegraph$cxxbridge1$ShimSceneGraph$create_camera_node(*this, translate_attrs, rotate_attrs, scale_attrs, camera_attrs, rotate_order, film_fit, render_image_width, render_image_height);
}

MMSCENEGRAPH_API_EXPORT ::mmscenegraph::MarkerNode ShimSceneGraph::create_marker_node(::mmscenegraph::MarkerAttrIds marker_attrs) noexcept {
  return mmscenegraph$cxxbridge1$ShimSceneGraph$create_marker_node(*this, marker_attrs);
}

MMSCENEGRAPH_API_EXPORT bool ShimSceneGraph::link_marker_to_camera(::mmscenegraph::NodeId mkr_node_id, ::mmscenegraph::NodeId cam_node_id) noexcept {
  return mmscenegraph$cxxbridge1$ShimSceneGraph$link_marker_to_camera(*this, mkr_node_id, cam_node_id);
}

MMSCENEGRAPH_API_EXPORT bool ShimSceneGraph::link_marker_to_bundle(::mmscenegraph::NodeId mkr_node_id, ::mmscenegraph::NodeId bnd_node_id) noexcept {
  return mmscenegraph$cxxbridge1$ShimSceneGraph$link_marker_to_bundle(*this, mkr_node_id, bnd_node_id);
}

MMSCENEGRAPH_API_EXPORT bool ShimSceneGraph::set_node_parent(::mmscenegraph::NodeId child_node_id, ::mmscenegraph::NodeId parent_node_id) noexcept {
  return mmscenegraph$cxxbridge1$ShimSceneGraph$set_node_parent(*this, child_node_id, parent_node_id);
}

MMSCENEGRAPH_API_EXPORT ::rust::Box<::mmscenegraph::ShimSceneGraph> shim_create_scene_graph_box() noexcept {
  return ::rust::Box<::mmscenegraph::ShimSceneGraph>::from_raw(mmscenegraph$cxxbridge1$shim_create_scene_graph_box());
}

::std::size_t ShimFlatScene::layout::size() noexcept {
  return mmscenegraph$cxxbridge1$ShimFlatScene$operator$sizeof();
}

::std::size_t ShimFlatScene::layout::align() noexcept {
  return mmscenegraph$cxxbridge1$ShimFlatScene$operator$alignof();
}

MMSCENEGRAPH_API_EXPORT ::rust::Slice<double const> ShimFlatScene::markers() const noexcept {
  return ::rust::impl<::rust::Slice<double const>>::slice(mmscenegraph$cxxbridge1$ShimFlatScene$markers(*this));
}

MMSCENEGRAPH_API_EXPORT ::rust::Slice<double const> ShimFlatScene::points() const noexcept {
  return ::rust::impl<::rust::Slice<double const>>::slice(mmscenegraph$cxxbridge1$ShimFlatScene$points(*this));
}

MMSCENEGRAPH_API_EXPORT ::std::size_t ShimFlatScene::num_markers() const noexcept {
  return mmscenegraph$cxxbridge1$ShimFlatScene$num_markers(*this);
}

MMSCENEGRAPH_API_EXPORT ::std::size_t ShimFlatScene::num_points() const noexcept {
  return mmscenegraph$cxxbridge1$ShimFlatScene$num_points(*this);
}

MMSCENEGRAPH_API_EXPORT void ShimFlatScene::evaluate(::rust::Box<::mmscenegraph::ShimAttrDataBlock> const &attrdb, ::rust::Slice<::std::uint32_t const> frame_list) noexcept {
  mmscenegraph$cxxbridge1$ShimFlatScene$evaluate(*this, attrdb, frame_list);
}

MMSCENEGRAPH_API_EXPORT ::rust::Box<::mmscenegraph::ShimFlatScene> shim_bake_scene_graph(::rust::Box<::mmscenegraph::ShimSceneGraph> const &sg, ::rust::Box<::mmscenegraph::ShimEvaluationObjects> const &eval_objects) noexcept {
  return ::rust::Box<::mmscenegraph::ShimFlatScene>::from_raw(mmscenegraph$cxxbridge1$shim_bake_scene_graph(sg, eval_objects));
}

MMSCENEGRAPH_API_EXPORT ::rust::Box<::mmscenegraph::ShimFlatScene> shim_create_flat_scene_box() noexcept {
  return ::rust::Box<::mmscenegraph::ShimFlatScene>::from_raw(mmscenegraph$cxxbridge1$shim_create_flat_scene_box());
}

::std::size_t ShimEvaluationObjects::layout::size() noexcept {
  return mmscenegraph$cxxbridge1$ShimEvaluationObjects$operator$sizeof();
}

::std::size_t ShimEvaluationObjects::layout::align() noexcept {
  return mmscenegraph$cxxbridge1$ShimEvaluationObjects$operator$alignof();
}

MMSCENEGRAPH_API_EXPORT void ShimEvaluationObjects::clear_all() noexcept {
  mmscenegraph$cxxbridge1$ShimEvaluationObjects$clear_all(*this);
}

MMSCENEGRAPH_API_EXPORT void ShimEvaluationObjects::clear_bundles() noexcept {
  mmscenegraph$cxxbridge1$ShimEvaluationObjects$clear_bundles(*this);
}

MMSCENEGRAPH_API_EXPORT void ShimEvaluationObjects::clear_markers() noexcept {
  mmscenegraph$cxxbridge1$ShimEvaluationObjects$clear_markers(*this);
}

MMSCENEGRAPH_API_EXPORT void ShimEvaluationObjects::clear_cameras() noexcept {
  mmscenegraph$cxxbridge1$ShimEvaluationObjects$clear_cameras(*this);
}

MMSCENEGRAPH_API_EXPORT ::std::size_t ShimEvaluationObjects::num_bundles() const noexcept {
  return mmscenegraph$cxxbridge1$ShimEvaluationObjects$num_bundles(*this);
}

MMSCENEGRAPH_API_EXPORT ::std::size_t ShimEvaluationObjects::num_markers() const noexcept {
  return mmscenegraph$cxxbridge1$ShimEvaluationObjects$num_markers(*this);
}

MMSCENEGRAPH_API_EXPORT ::std::size_t ShimEvaluationObjects::num_cameras() const noexcept {
  return mmscenegraph$cxxbridge1$ShimEvaluationObjects$num_cameras(*this);
}

MMSCENEGRAPH_API_EXPORT void ShimEvaluationObjects::add_bundle(::mmscenegraph::BundleNode const &bnd_node) noexcept {
  mmscenegraph$cxxbridge1$ShimEvaluationObjects$add_bundle(*this, bnd_node);
}

MMSCENEGRAPH_API_EXPORT void ShimEvaluationObjects::add_camera(::mmscenegraph::CameraNode const &cam_node) noexcept {
  mmscenegraph$cxxbridge1$ShimEvaluationObjects$add_camera(*this, cam_node);
}

MMSCENEGRAPH_API_EXPORT void ShimEvaluationObjects::add_marker(::mmscenegraph::MarkerNode const &mkr_node) noexcept {
  mmscenegraph$cxxbridge1$ShimEvaluationObjects$add_marker(*this, mkr_node);
}

MMSCENEGRAPH_API_EXPORT ::rust::Box<::mmscenegraph::ShimEvaluationObjects> shim_create_evaluation_objects_box() noexcept {
  return ::rust::Box<::mmscenegraph::ShimEvaluationObjects>::from_raw(mmscenegraph$cxxbridge1$shim_create_evaluation_objects_box());
}

MMSCENEGRAPH_API_EXPORT bool shim_fit_line_to_points_type2(::rust::Slice<double const> x, ::rust::Slice<double const> y, double &out_point_x, double &out_point_y, double &out_dir_x, double &out_dir_y) noexcept {
  return mmscenegraph$cxxbridge1$shim_fit_line_to_points_type2(x, y, out_point_x, out_point_y, out_dir_x, out_dir_y);
}

MMSCENEGRAPH_API_EXPORT bool shim_fit_straight_line_to_ordered_points(::rust::Slice<double const> points_coord_x, ::rust::Slice<double const> points_coord_y, double &out_point_x, double &out_point_y, double &out_dir_x, double &out_dir_y) noexcept {
  return mmscenegraph$cxxbridge1$shim_fit_straight_line_to_ordered_points(points_coord_x, points_coord_y, out_point_x, out_point_y, out_dir_x, out_dir_y);
}

MMSCENEGRAPH_API_EXPORT bool shim_line_point_intersection(::mmscenegraph::Point3 point, ::mmscenegraph::Point3 line_a, ::mmscenegraph::Point3 line_b, ::mmscenegraph::Point3 &out_point) noexcept {
  return mmscenegraph$cxxbridge1$shim_line_point_intersection(point, line_a, line_b, out_point);
}

MMSCENEGRAPH_API_EXPORT bool shim_fit_plane_to_points(::rust::Slice<double const> points_xyz, double &out_point_x, double &out_point_y, double &out_point_z, double &out_dir_x, double &out_dir_y, double &out_dir_z, double &out_scale, double &out_rms_error) noexcept {
  return mmscenegraph$cxxbridge1$shim_fit_plane_to_points(points_xyz, out_point_x, out_point_y, out_point_z, out_dir_x, out_dir_y, out_dir_z, out_scale, out_rms_error);
}

MMSCENEGRAPH_API_EXPORT bool shim_detect_curve_pops(::rust::Slice<double const> x_values, ::rust::Slice<double const> y_values, double threshold, ::rust::Vec<double> &out_x_values, ::rust::Vec<double> &out_y_values) noexcept {
  return mmscenegraph$cxxbridge1$shim_detect_curve_pops(x_values, y_values, threshold, out_x_values, out_y_values);
}

MMSCENEGRAPH_API_EXPORT bool shim_filter_curve_pops(::rust::Slice<double const> x_values, ::rust::Slice<double const> y_values, double threshold, ::rust::Vec<double> &out_x_values, ::rust::Vec<double> &out_y_values) noexcept {
  return mmscenegraph$cxxbridge1$shim_filter_curve_pops(x_values, y_values, threshold, out_x_values, out_y_values);
}

MMSCENEGRAPH_API_EXPORT bool shim_curve_simplify(::rust::Slice<double const> x_values, ::rust::Slice<double const> y_values, ::std::size_t control_point_count, ::mmscenegraph::ControlPointDistribution distribution, ::mmscenegraph::Interpolation interpolation_method, ::rust::Vec<double> &out_x_values, ::rust::Vec<double> &out_y_values) noexcept {
  return mmscenegraph$cxxbridge1$shim_curve_simplify(x_values, y_values, control_point_count, distribution, interpolation_method, out_x_values, out_y_values);
}

MMSCENEGRAPH_API_EXPORT double shim_gaussian(double x, double mean, double sigma) noexcept {
  return mmscenegraph$cxxbridge1$shim_gaussian(x, mean, sigma);
}

MMSCENEGRAPH_API_EXPORT bool shim_calc_mean_absolute_deviation(::rust::Slice<double const> data, double &out_mean) noexcept {
  return mmscenegraph$cxxbridge1$shim_calc_mean_absolute_deviation(data, out_mean);
}

MMSCENEGRAPH_API_EXPORT bool shim_calc_population_variance(::rust::Slice<double const> data, double &out_mean, double &out_variance) noexcept {
  return mmscenegraph$cxxbridge1$shim_calc_population_variance(data, out_mean, out_variance);
}

MMSCENEGRAPH_API_EXPORT bool shim_calc_sample_variance(::rust::Slice<double const> data, double &out_mean, double &out_variance) noexcept {
  return mmscenegraph$cxxbridge1$shim_calc_sample_variance(data, out_mean, out_variance);
}

MMSCENEGRAPH_API_EXPORT bool shim_calc_population_standard_deviation(::rust::Slice<double const> data, double &out_mean, double &out_std_dev) noexcept {
  return mmscenegraph$cxxbridge1$shim_calc_population_standard_deviation(data, out_mean, out_std_dev);
}

MMSCENEGRAPH_API_EXPORT bool shim_calc_sample_standard_deviation(::rust::Slice<double const> data, double &out_mean, double &out_std_dev) noexcept {
  return mmscenegraph$cxxbridge1$shim_calc_sample_standard_deviation(data, out_mean, out_std_dev);
}

MMSCENEGRAPH_API_EXPORT bool shim_calc_population_coefficient_of_variation(::rust::Slice<double const> data, double &out_mean, double &out_cv) noexcept {
  return mmscenegraph$cxxbridge1$shim_calc_population_coefficient_of_variation(data, out_mean, out_cv);
}

MMSCENEGRAPH_API_EXPORT bool shim_calc_sample_coefficient_of_variation(::rust::Slice<double const> data, double &out_mean, double &out_cv) noexcept {
  return mmscenegraph$cxxbridge1$shim_calc_sample_coefficient_of_variation(data, out_mean, out_cv);
}

MMSCENEGRAPH_API_EXPORT bool shim_calc_population_relative_standard_deviation(::rust::Slice<double const> data, double &out_mean, double &out_rsd) noexcept {
  return mmscenegraph$cxxbridge1$shim_calc_population_relative_standard_deviation(data, out_mean, out_rsd);
}

MMSCENEGRAPH_API_EXPORT bool shim_calc_sample_relative_standard_deviation(::rust::Slice<double const> data, double &out_mean, double &out_rsd) noexcept {
  return mmscenegraph$cxxbridge1$shim_calc_sample_relative_standard_deviation(data, out_mean, out_rsd);
}

MMSCENEGRAPH_API_EXPORT double shim_calc_z_score(double mean, double std_dev, double value) noexcept {
  return mmscenegraph$cxxbridge1$shim_calc_z_score(mean, std_dev, value);
}

MMSCENEGRAPH_API_EXPORT bool shim_calc_peak_to_peak(::rust::Slice<double const> data, double &out_value) noexcept {
  return mmscenegraph$cxxbridge1$shim_calc_peak_to_peak(data, out_value);
}

MMSCENEGRAPH_API_EXPORT bool shim_calc_skewness_type1(::rust::Slice<double const> data, double &out_mean, double &out_skewness) noexcept {
  return mmscenegraph$cxxbridge1$shim_calc_skewness_type1(data, out_mean, out_skewness);
}

MMSCENEGRAPH_API_EXPORT bool shim_calc_skewness_type2(::rust::Slice<double const> data, double &out_mean, double &out_skewness) noexcept {
  return mmscenegraph$cxxbridge1$shim_calc_skewness_type2(data, out_mean, out_skewness);
}

MMSCENEGRAPH_API_EXPORT bool shim_calc_population_kurtosis_excess(::rust::Slice<double const> data, double &out_mean, double &out_kurtosis) noexcept {
  return mmscenegraph$cxxbridge1$shim_calc_population_kurtosis_excess(data, out_mean, out_kurtosis);
}

MMSCENEGRAPH_API_EXPORT bool shim_calc_sample_kurtosis_excess(::rust::Slice<double const> data, double &out_mean, double &out_kurtosis) noexcept {
  return mmscenegraph$cxxbridge1$shim_calc_sample_kurtosis_excess(data, out_mean, out_kurtosis);
}

MMSCENEGRAPH_API_EXPORT bool shim_calc_local_minima_maxima(::rust::Slice<double const> data, ::rust::Vec<::std::size_t> &out_indices) noexcept {
  return mmscenegraph$cxxbridge1$shim_calc_local_minima_maxima(data, out_indices);
}

MMSCENEGRAPH_API_EXPORT bool shim_calc_signal_to_noise_ratio(::rust::Slice<double const> data, double &out_mean, double &out_snr) noexcept {
  return mmscenegraph$cxxbridge1$shim_calc_signal_to_noise_ratio(data, out_mean, out_snr);
}

MMSCENEGRAPH_API_EXPORT bool shim_calc_signal_to_noise_ratio_as_decibels(::rust::Slice<double const> data, double &out_mean, double &out_snr_db) noexcept {
  return mmscenegraph$cxxbridge1$shim_calc_signal_to_noise_ratio_as_decibels(data, out_mean, out_snr_db);
}

MMSCENEGRAPH_API_EXPORT bool shim_calc_median_absolute_deviation(::rust::Slice<double const> sorted_data, double &out_median, double &out_mad) noexcept {
  return mmscenegraph$cxxbridge1$shim_calc_median_absolute_deviation(sorted_data, out_median, out_mad);
}

MMSCENEGRAPH_API_EXPORT bool shim_calc_median_absolute_deviation_sigma(double value, ::rust::Slice<double const> sorted_data, double &out_median, double &out_sigma) noexcept {
  return mmscenegraph$cxxbridge1$shim_calc_median_absolute_deviation_sigma(value, sorted_data, out_median, out_sigma);
}

MMSCENEGRAPH_API_EXPORT bool shim_calc_quantile(::rust::Slice<double const> sorted_data, double probability, double &out_value) noexcept {
  return mmscenegraph$cxxbridge1$shim_calc_quantile(sorted_data, probability, out_value);
}

MMSCENEGRAPH_API_EXPORT bool shim_calc_quartiles(::rust::Slice<double const> sorted_data, double &out_q1, double &out_q2, double &out_q3) noexcept {
  return mmscenegraph$cxxbridge1$shim_calc_quartiles(sorted_data, out_q1, out_q2, out_q3);
}

MMSCENEGRAPH_API_EXPORT bool shim_calc_interquartile_range(::rust::Slice<double const> sorted_data, double &out_median, double &out_iqr) noexcept {
  return mmscenegraph$cxxbridge1$shim_calc_interquartile_range(sorted_data, out_median, out_iqr);
}

MMSCENEGRAPH_API_EXPORT bool shim_calc_percentile_rank(::rust::Slice<double const> sorted_data, double value, double &out_rank) noexcept {
  return mmscenegraph$cxxbridge1$shim_calc_percentile_rank(sorted_data, value, out_rank);
}

MMSCENEGRAPH_API_EXPORT bool shim_calc_mean_absolute_error(::rust::Slice<double const> actual, ::rust::Slice<double const> predicted, double &out_mae) noexcept {
  return mmscenegraph$cxxbridge1$shim_calc_mean_absolute_error(actual, predicted, out_mae);
}

MMSCENEGRAPH_API_EXPORT bool shim_calc_root_mean_square_error(::rust::Slice<double const> actual, ::rust::Slice<double const> predicted, double &out_rmse) noexcept {
  return mmscenegraph$cxxbridge1$shim_calc_root_mean_square_error(actual, predicted, out_rmse);
}

MMSCENEGRAPH_API_EXPORT bool shim_calc_normalized_root_mean_square_error(::rust::Slice<double const> actual, ::rust::Slice<double const> predicted, double &out_nrmse) noexcept {
  return mmscenegraph$cxxbridge1$shim_calc_normalized_root_mean_square_error(actual, predicted, out_nrmse);
}

MMSCENEGRAPH_API_EXPORT bool shim_calc_coefficient_of_determination(::rust::Slice<double const> actual, ::rust::Slice<double const> predicted, double &out_r_squared) noexcept {
  return mmscenegraph$cxxbridge1$shim_calc_coefficient_of_determination(actual, predicted, out_r_squared);
}
} // namespace mmscenegraph

extern "C" {
::mmscenegraph::ShimAttrDataBlock *cxxbridge1$box$mmscenegraph$ShimAttrDataBlock$alloc() noexcept;
void cxxbridge1$box$mmscenegraph$ShimAttrDataBlock$dealloc(::mmscenegraph::ShimAttrDataBlock *) noexcept;
void cxxbridge1$box$mmscenegraph$ShimAttrDataBlock$drop(::rust::Box<::mmscenegraph::ShimAttrDataBlock> *ptr) noexcept;

::mmscenegraph::ShimSceneGraph *cxxbridge1$box$mmscenegraph$ShimSceneGraph$alloc() noexcept;
void cxxbridge1$box$mmscenegraph$ShimSceneGraph$dealloc(::mmscenegraph::ShimSceneGraph *) noexcept;
void cxxbridge1$box$mmscenegraph$ShimSceneGraph$drop(::rust::Box<::mmscenegraph::ShimSceneGraph> *ptr) noexcept;

::mmscenegraph::ShimEvaluationObjects *cxxbridge1$box$mmscenegraph$ShimEvaluationObjects$alloc() noexcept;
void cxxbridge1$box$mmscenegraph$ShimEvaluationObjects$dealloc(::mmscenegraph::ShimEvaluationObjects *) noexcept;
void cxxbridge1$box$mmscenegraph$ShimEvaluationObjects$drop(::rust::Box<::mmscenegraph::ShimEvaluationObjects> *ptr) noexcept;

::mmscenegraph::ShimFlatScene *cxxbridge1$box$mmscenegraph$ShimFlatScene$alloc() noexcept;
void cxxbridge1$box$mmscenegraph$ShimFlatScene$dealloc(::mmscenegraph::ShimFlatScene *) noexcept;
void cxxbridge1$box$mmscenegraph$ShimFlatScene$drop(::rust::Box<::mmscenegraph::ShimFlatScene> *ptr) noexcept;
} // extern "C"

namespace rust {
inline namespace cxxbridge1 {
template <>
MMSCENEGRAPH_API_EXPORT ::mmscenegraph::ShimAttrDataBlock *Box<::mmscenegraph::ShimAttrDataBlock>::allocation::alloc() noexcept {
  return cxxbridge1$box$mmscenegraph$ShimAttrDataBlock$alloc();
}
template <>
MMSCENEGRAPH_API_EXPORT void Box<::mmscenegraph::ShimAttrDataBlock>::allocation::dealloc(::mmscenegraph::ShimAttrDataBlock *ptr) noexcept {
  cxxbridge1$box$mmscenegraph$ShimAttrDataBlock$dealloc(ptr);
}
template <>
MMSCENEGRAPH_API_EXPORT void Box<::mmscenegraph::ShimAttrDataBlock>::drop() noexcept {
  cxxbridge1$box$mmscenegraph$ShimAttrDataBlock$drop(this);
}
template <>
MMSCENEGRAPH_API_EXPORT ::mmscenegraph::ShimSceneGraph *Box<::mmscenegraph::ShimSceneGraph>::allocation::alloc() noexcept {
  return cxxbridge1$box$mmscenegraph$ShimSceneGraph$alloc();
}
template <>
MMSCENEGRAPH_API_EXPORT void Box<::mmscenegraph::ShimSceneGraph>::allocation::dealloc(::mmscenegraph::ShimSceneGraph *ptr) noexcept {
  cxxbridge1$box$mmscenegraph$ShimSceneGraph$dealloc(ptr);
}
template <>
MMSCENEGRAPH_API_EXPORT void Box<::mmscenegraph::ShimSceneGraph>::drop() noexcept {
  cxxbridge1$box$mmscenegraph$ShimSceneGraph$drop(this);
}
template <>
MMSCENEGRAPH_API_EXPORT ::mmscenegraph::ShimEvaluationObjects *Box<::mmscenegraph::ShimEvaluationObjects>::allocation::alloc() noexcept {
  return cxxbridge1$box$mmscenegraph$ShimEvaluationObjects$alloc();
}
template <>
MMSCENEGRAPH_API_EXPORT void Box<::mmscenegraph::ShimEvaluationObjects>::allocation::dealloc(::mmscenegraph::ShimEvaluationObjects *ptr) noexcept {
  cxxbridge1$box$mmscenegraph$ShimEvaluationObjects$dealloc(ptr);
}
template <>
MMSCENEGRAPH_API_EXPORT void Box<::mmscenegraph::ShimEvaluationObjects>::drop() noexcept {
  cxxbridge1$box$mmscenegraph$ShimEvaluationObjects$drop(this);
}
template <>
MMSCENEGRAPH_API_EXPORT ::mmscenegraph::ShimFlatScene *Box<::mmscenegraph::ShimFlatScene>::allocation::alloc() noexcept {
  return cxxbridge1$box$mmscenegraph$ShimFlatScene$alloc();
}
template <>
MMSCENEGRAPH_API_EXPORT void Box<::mmscenegraph::ShimFlatScene>::allocation::dealloc(::mmscenegraph::ShimFlatScene *ptr) noexcept {
  cxxbridge1$box$mmscenegraph$ShimFlatScene$dealloc(ptr);
}
template <>
MMSCENEGRAPH_API_EXPORT void Box<::mmscenegraph::ShimFlatScene>::drop() noexcept {
  cxxbridge1$box$mmscenegraph$ShimFlatScene$drop(this);
}
} // namespace cxxbridge1
} // namespace rust
