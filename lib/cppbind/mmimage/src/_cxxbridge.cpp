#include "mmimage/_cxx.h"
#include "mmimage/_symbol_export.h"
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
#include <string>
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

struct unsafe_bitcopy_t;

namespace {
template <typename T>
class impl;
} // namespace

template <typename T>
::std::size_t size_of();
template <typename T>
::std::size_t align_of();

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

class Str::uninit {};
inline Str::Str(uninit) noexcept {}

template <typename T>
class Slice<T>::uninit {};
template <typename T>
inline Slice<T>::Slice(uninit) noexcept {}

namespace repr {
using Fat = ::std::array<::std::uintptr_t, 2>;
} // namespace repr

namespace detail {
template <typename T, typename = void *>
struct operator_new {
  void *operator()(::std::size_t sz) { return ::operator new(sz); }
};

template <typename T>
struct operator_new<T, decltype(T::operator new(sizeof(T)))> {
  void *operator()(::std::size_t sz) { return T::operator new(sz); }
};
} // namespace detail

template <typename T>
union MaybeUninit {
  T value;
  void *operator new(::std::size_t sz) { return detail::operator_new<T>{}(sz); }
  MaybeUninit() {}
  ~MaybeUninit() {}
};

namespace {
template <>
class impl<Str> final {
public:
  static Str new_unchecked(repr::Fat repr) noexcept {
    Str str = Str::uninit{};
    str.repr = repr;
    return str;
  }
};

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

namespace mmimage {
  enum class AttributeValueType : ::std::uint8_t;
  enum class ExrCompression : ::std::uint8_t;
  enum class ExrPixelLayoutMode : ::std::uint8_t;
  struct ExrPixelLayout;
  enum class ExrLineOrder : ::std::uint8_t;
  struct ImageExrEncoder;
  struct OptionF32;
  struct Vec2F32;
  struct Vec2I32;
  struct Box2F32;
  struct ImageRegionRectangle;
  struct PixelF32x4;
  struct PixelF64x2;
  enum class BufferDataType : ::std::uint8_t;
  struct ShimImagePixelBuffer;
  struct ShimImageMetaData;
}

namespace mmimage {
#ifndef CXXBRIDGE1_ENUM_mmimage$AttributeValueType
#define CXXBRIDGE1_ENUM_mmimage$AttributeValueType
enum class AttributeValueType : ::std::uint8_t {
  kNone = 0,
  kString = 1,
  kF32 = 2,
  kF64 = 3,
  kI32 = 4,
  kVec2F32 = 5,
  kVec2I32 = 6,
  kVec3F32 = 7,
  kVec3I32 = 8,
  kBox2F32 = 9,
  kUnknown = 255,
};
#endif // CXXBRIDGE1_ENUM_mmimage$AttributeValueType

#ifndef CXXBRIDGE1_ENUM_mmimage$ExrCompression
#define CXXBRIDGE1_ENUM_mmimage$ExrCompression
enum class ExrCompression : ::std::uint8_t {
  kUncompressed = 0,
  kRLE = 1,
  kZIP1 = 2,
  kZIP16 = 3,
  kPIZ = 4,
  kPXR24 = 5,
  kB44 = 6,
  kB44A = 7,
  kUnknown = 255,
};
#endif // CXXBRIDGE1_ENUM_mmimage$ExrCompression

#ifndef CXXBRIDGE1_ENUM_mmimage$ExrPixelLayoutMode
#define CXXBRIDGE1_ENUM_mmimage$ExrPixelLayoutMode
enum class ExrPixelLayoutMode : ::std::uint8_t {
  kScanLines = 0,
  kTiles = 1,
  kUnknown = 255,
};
#endif // CXXBRIDGE1_ENUM_mmimage$ExrPixelLayoutMode

#ifndef CXXBRIDGE1_STRUCT_mmimage$ExrPixelLayout
#define CXXBRIDGE1_STRUCT_mmimage$ExrPixelLayout
struct ExrPixelLayout final {
  ::mmimage::ExrPixelLayoutMode mode;
  ::std::size_t tile_size_x;
  ::std::size_t tile_size_y;

  bool operator==(ExrPixelLayout const &) const noexcept;
  bool operator!=(ExrPixelLayout const &) const noexcept;
  bool operator<(ExrPixelLayout const &) const noexcept;
  bool operator<=(ExrPixelLayout const &) const noexcept;
  bool operator>(ExrPixelLayout const &) const noexcept;
  bool operator>=(ExrPixelLayout const &) const noexcept;
  using IsRelocatable = ::std::true_type;
};
#endif // CXXBRIDGE1_STRUCT_mmimage$ExrPixelLayout

#ifndef CXXBRIDGE1_ENUM_mmimage$ExrLineOrder
#define CXXBRIDGE1_ENUM_mmimage$ExrLineOrder
enum class ExrLineOrder : ::std::uint8_t {
  kIncreasing = 0,
  kDecreasing = 1,
  kUnspecified = 2,
  kUnknown = 255,
};
#endif // CXXBRIDGE1_ENUM_mmimage$ExrLineOrder

#ifndef CXXBRIDGE1_STRUCT_mmimage$ImageExrEncoder
#define CXXBRIDGE1_STRUCT_mmimage$ImageExrEncoder
struct ImageExrEncoder final {
  ::mmimage::ExrCompression compression;
  ::mmimage::ExrPixelLayout pixel_layout;
  ::mmimage::ExrLineOrder line_order;

  bool operator==(ImageExrEncoder const &) const noexcept;
  bool operator!=(ImageExrEncoder const &) const noexcept;
  bool operator<(ImageExrEncoder const &) const noexcept;
  bool operator<=(ImageExrEncoder const &) const noexcept;
  bool operator>(ImageExrEncoder const &) const noexcept;
  bool operator>=(ImageExrEncoder const &) const noexcept;
  using IsRelocatable = ::std::true_type;
};
#endif // CXXBRIDGE1_STRUCT_mmimage$ImageExrEncoder

#ifndef CXXBRIDGE1_STRUCT_mmimage$OptionF32
#define CXXBRIDGE1_STRUCT_mmimage$OptionF32
struct OptionF32 final {
  bool exists;
  float value;

  bool operator==(OptionF32 const &) const noexcept;
  bool operator!=(OptionF32 const &) const noexcept;
  bool operator<(OptionF32 const &) const noexcept;
  bool operator<=(OptionF32 const &) const noexcept;
  bool operator>(OptionF32 const &) const noexcept;
  bool operator>=(OptionF32 const &) const noexcept;
  using IsRelocatable = ::std::true_type;
};
#endif // CXXBRIDGE1_STRUCT_mmimage$OptionF32

#ifndef CXXBRIDGE1_STRUCT_mmimage$Vec2F32
#define CXXBRIDGE1_STRUCT_mmimage$Vec2F32
struct Vec2F32 final {
  float x;
  float y;

  bool operator==(Vec2F32 const &) const noexcept;
  bool operator!=(Vec2F32 const &) const noexcept;
  bool operator<(Vec2F32 const &) const noexcept;
  bool operator<=(Vec2F32 const &) const noexcept;
  bool operator>(Vec2F32 const &) const noexcept;
  bool operator>=(Vec2F32 const &) const noexcept;
  using IsRelocatable = ::std::true_type;
};
#endif // CXXBRIDGE1_STRUCT_mmimage$Vec2F32

#ifndef CXXBRIDGE1_STRUCT_mmimage$Vec2I32
#define CXXBRIDGE1_STRUCT_mmimage$Vec2I32
struct Vec2I32 final {
  ::std::int32_t x;
  ::std::int32_t y;

  bool operator==(Vec2I32 const &) const noexcept;
  bool operator!=(Vec2I32 const &) const noexcept;
  bool operator<(Vec2I32 const &) const noexcept;
  bool operator<=(Vec2I32 const &) const noexcept;
  bool operator>(Vec2I32 const &) const noexcept;
  bool operator>=(Vec2I32 const &) const noexcept;
  using IsRelocatable = ::std::true_type;
};
#endif // CXXBRIDGE1_STRUCT_mmimage$Vec2I32

#ifndef CXXBRIDGE1_STRUCT_mmimage$Box2F32
#define CXXBRIDGE1_STRUCT_mmimage$Box2F32
struct Box2F32 final {
  float min_x;
  float min_y;
  float max_x;
  float max_y;

  bool operator==(Box2F32 const &) const noexcept;
  bool operator!=(Box2F32 const &) const noexcept;
  bool operator<(Box2F32 const &) const noexcept;
  bool operator<=(Box2F32 const &) const noexcept;
  bool operator>(Box2F32 const &) const noexcept;
  bool operator>=(Box2F32 const &) const noexcept;
  using IsRelocatable = ::std::true_type;
};
#endif // CXXBRIDGE1_STRUCT_mmimage$Box2F32

#ifndef CXXBRIDGE1_STRUCT_mmimage$ImageRegionRectangle
#define CXXBRIDGE1_STRUCT_mmimage$ImageRegionRectangle
struct ImageRegionRectangle final {
  ::std::int32_t position_x;
  ::std::int32_t position_y;
  ::std::size_t size_x;
  ::std::size_t size_y;

  bool operator==(ImageRegionRectangle const &) const noexcept;
  bool operator!=(ImageRegionRectangle const &) const noexcept;
  bool operator<(ImageRegionRectangle const &) const noexcept;
  bool operator<=(ImageRegionRectangle const &) const noexcept;
  bool operator>(ImageRegionRectangle const &) const noexcept;
  bool operator>=(ImageRegionRectangle const &) const noexcept;
  using IsRelocatable = ::std::true_type;
};
#endif // CXXBRIDGE1_STRUCT_mmimage$ImageRegionRectangle

#ifndef CXXBRIDGE1_STRUCT_mmimage$PixelF32x4
#define CXXBRIDGE1_STRUCT_mmimage$PixelF32x4
struct PixelF32x4 final {
  float r;
  float g;
  float b;
  float a;

  bool operator==(PixelF32x4 const &) const noexcept;
  bool operator!=(PixelF32x4 const &) const noexcept;
  bool operator<(PixelF32x4 const &) const noexcept;
  bool operator<=(PixelF32x4 const &) const noexcept;
  bool operator>(PixelF32x4 const &) const noexcept;
  bool operator>=(PixelF32x4 const &) const noexcept;
  using IsRelocatable = ::std::true_type;
};
#endif // CXXBRIDGE1_STRUCT_mmimage$PixelF32x4

#ifndef CXXBRIDGE1_STRUCT_mmimage$PixelF64x2
#define CXXBRIDGE1_STRUCT_mmimage$PixelF64x2
struct PixelF64x2 final {
  double x;
  double y;

  bool operator==(PixelF64x2 const &) const noexcept;
  bool operator!=(PixelF64x2 const &) const noexcept;
  bool operator<(PixelF64x2 const &) const noexcept;
  bool operator<=(PixelF64x2 const &) const noexcept;
  bool operator>(PixelF64x2 const &) const noexcept;
  bool operator>=(PixelF64x2 const &) const noexcept;
  using IsRelocatable = ::std::true_type;
};
#endif // CXXBRIDGE1_STRUCT_mmimage$PixelF64x2

#ifndef CXXBRIDGE1_ENUM_mmimage$BufferDataType
#define CXXBRIDGE1_ENUM_mmimage$BufferDataType
enum class BufferDataType : ::std::uint8_t {
  kNone = 0,
  kF16 = 1,
  kF32 = 2,
  kF64 = 3,
};
#endif // CXXBRIDGE1_ENUM_mmimage$BufferDataType

#ifndef CXXBRIDGE1_STRUCT_mmimage$ShimImagePixelBuffer
#define CXXBRIDGE1_STRUCT_mmimage$ShimImagePixelBuffer
struct ShimImagePixelBuffer final : public ::rust::Opaque {
  MMIMAGE_API_EXPORT ::mmimage::BufferDataType data_type() const noexcept;
  MMIMAGE_API_EXPORT ::std::size_t image_width() const noexcept;
  MMIMAGE_API_EXPORT ::std::size_t image_height() const noexcept;
  MMIMAGE_API_EXPORT ::std::size_t num_channels() const noexcept;
  MMIMAGE_API_EXPORT ::std::size_t pixel_count() const noexcept;
  MMIMAGE_API_EXPORT ::std::size_t element_count() const noexcept;
  MMIMAGE_API_EXPORT ::rust::Slice<::mmimage::PixelF32x4 const> as_slice_f32x4() const noexcept;
  MMIMAGE_API_EXPORT ::rust::Slice<::mmimage::PixelF32x4 > as_slice_f32x4_mut() noexcept;
  MMIMAGE_API_EXPORT void resize(::mmimage::BufferDataType data_type, ::std::size_t image_width, ::std::size_t image_height, ::std::size_t num_channels) noexcept;
  ~ShimImagePixelBuffer() = delete;

private:
  friend ::rust::layout;
  struct layout {
    static ::std::size_t size() noexcept;
    static ::std::size_t align() noexcept;
  };
};
#endif // CXXBRIDGE1_STRUCT_mmimage$ShimImagePixelBuffer

#ifndef CXXBRIDGE1_STRUCT_mmimage$ShimImageMetaData
#define CXXBRIDGE1_STRUCT_mmimage$ShimImageMetaData
struct ShimImageMetaData final : public ::rust::Opaque {
  MMIMAGE_API_EXPORT ::mmimage::ImageRegionRectangle get_display_window() const noexcept;
  MMIMAGE_API_EXPORT void set_display_window(::mmimage::ImageRegionRectangle value) noexcept;
  MMIMAGE_API_EXPORT float get_pixel_aspect() const noexcept;
  MMIMAGE_API_EXPORT void set_pixel_aspect(float value) noexcept;
  MMIMAGE_API_EXPORT ::rust::Str get_layer_name() const noexcept;
  MMIMAGE_API_EXPORT void set_layer_name(::rust::Str value) noexcept;
  MMIMAGE_API_EXPORT ::mmimage::Vec2I32 get_layer_position() const noexcept;
  MMIMAGE_API_EXPORT void set_layer_position(::mmimage::Vec2I32 value) noexcept;
  MMIMAGE_API_EXPORT ::mmimage::Vec2F32 get_screen_window_center() const noexcept;
  MMIMAGE_API_EXPORT void set_screen_window_center(::mmimage::Vec2F32 value) noexcept;
  MMIMAGE_API_EXPORT float get_screen_window_width() const noexcept;
  MMIMAGE_API_EXPORT void set_screen_window_width(float value) noexcept;
  MMIMAGE_API_EXPORT ::rust::Str get_owner() const noexcept;
  MMIMAGE_API_EXPORT void set_owner(::rust::Str value) noexcept;
  MMIMAGE_API_EXPORT ::rust::Str get_comments() const noexcept;
  MMIMAGE_API_EXPORT void set_comments(::rust::Str value) noexcept;
  MMIMAGE_API_EXPORT ::rust::Str get_capture_date() const noexcept;
  MMIMAGE_API_EXPORT ::mmimage::OptionF32 get_utc_offset() const noexcept;
  MMIMAGE_API_EXPORT ::mmimage::OptionF32 get_longitude() const noexcept;
  MMIMAGE_API_EXPORT ::mmimage::OptionF32 get_latitude() const noexcept;
  MMIMAGE_API_EXPORT ::mmimage::OptionF32 get_altitude() const noexcept;
  MMIMAGE_API_EXPORT ::mmimage::OptionF32 get_focus() const noexcept;
  MMIMAGE_API_EXPORT ::mmimage::OptionF32 get_exposure() const noexcept;
  MMIMAGE_API_EXPORT ::mmimage::OptionF32 get_aperture() const noexcept;
  MMIMAGE_API_EXPORT ::mmimage::OptionF32 get_iso_speed() const noexcept;
  MMIMAGE_API_EXPORT ::mmimage::OptionF32 get_frames_per_second() const noexcept;
  MMIMAGE_API_EXPORT ::rust::Str get_software_name() const noexcept;
  MMIMAGE_API_EXPORT void set_software_name(::rust::Str value) noexcept;
  MMIMAGE_API_EXPORT ::rust::Vec<::rust::String> all_named_attribute_names() const noexcept;
  MMIMAGE_API_EXPORT bool has_named_attribute(::rust::Str attribute_name) const noexcept;
  MMIMAGE_API_EXPORT ::std::uint8_t get_named_attribute_type_index(::rust::Str attribute_name) const noexcept;
  MMIMAGE_API_EXPORT ::std::int32_t get_named_attribute_as_i32(::rust::Str attribute_name) const noexcept;
  MMIMAGE_API_EXPORT float get_named_attribute_as_f32(::rust::Str attribute_name) const noexcept;
  MMIMAGE_API_EXPORT double get_named_attribute_as_f64(::rust::Str attribute_name) const noexcept;
  MMIMAGE_API_EXPORT ::rust::String get_named_attribute_as_string(::rust::Str attribute_name) const noexcept;
  MMIMAGE_API_EXPORT ::rust::String as_string() const noexcept;
  ~ShimImageMetaData() = delete;

private:
  friend ::rust::layout;
  struct layout {
    static ::std::size_t size() noexcept;
    static ::std::size_t align() noexcept;
  };
};
#endif // CXXBRIDGE1_STRUCT_mmimage$ShimImageMetaData

extern "C" {
bool mmimage$cxxbridge1$ExrPixelLayout$operator$eq(ExrPixelLayout const &, ExrPixelLayout const &) noexcept;
bool mmimage$cxxbridge1$ExrPixelLayout$operator$ne(ExrPixelLayout const &, ExrPixelLayout const &) noexcept;
bool mmimage$cxxbridge1$ExrPixelLayout$operator$lt(ExrPixelLayout const &, ExrPixelLayout const &) noexcept;
bool mmimage$cxxbridge1$ExrPixelLayout$operator$le(ExrPixelLayout const &, ExrPixelLayout const &) noexcept;
bool mmimage$cxxbridge1$ExrPixelLayout$operator$gt(ExrPixelLayout const &, ExrPixelLayout const &) noexcept;
bool mmimage$cxxbridge1$ExrPixelLayout$operator$ge(ExrPixelLayout const &, ExrPixelLayout const &) noexcept;
bool mmimage$cxxbridge1$ImageExrEncoder$operator$eq(ImageExrEncoder const &, ImageExrEncoder const &) noexcept;
bool mmimage$cxxbridge1$ImageExrEncoder$operator$ne(ImageExrEncoder const &, ImageExrEncoder const &) noexcept;
bool mmimage$cxxbridge1$ImageExrEncoder$operator$lt(ImageExrEncoder const &, ImageExrEncoder const &) noexcept;
bool mmimage$cxxbridge1$ImageExrEncoder$operator$le(ImageExrEncoder const &, ImageExrEncoder const &) noexcept;
bool mmimage$cxxbridge1$ImageExrEncoder$operator$gt(ImageExrEncoder const &, ImageExrEncoder const &) noexcept;
bool mmimage$cxxbridge1$ImageExrEncoder$operator$ge(ImageExrEncoder const &, ImageExrEncoder const &) noexcept;
bool mmimage$cxxbridge1$OptionF32$operator$eq(OptionF32 const &, OptionF32 const &) noexcept;
bool mmimage$cxxbridge1$OptionF32$operator$ne(OptionF32 const &, OptionF32 const &) noexcept;
bool mmimage$cxxbridge1$OptionF32$operator$lt(OptionF32 const &, OptionF32 const &) noexcept;
bool mmimage$cxxbridge1$OptionF32$operator$le(OptionF32 const &, OptionF32 const &) noexcept;
bool mmimage$cxxbridge1$OptionF32$operator$gt(OptionF32 const &, OptionF32 const &) noexcept;
bool mmimage$cxxbridge1$OptionF32$operator$ge(OptionF32 const &, OptionF32 const &) noexcept;
bool mmimage$cxxbridge1$Vec2F32$operator$eq(Vec2F32 const &, Vec2F32 const &) noexcept;
bool mmimage$cxxbridge1$Vec2F32$operator$ne(Vec2F32 const &, Vec2F32 const &) noexcept;
bool mmimage$cxxbridge1$Vec2F32$operator$lt(Vec2F32 const &, Vec2F32 const &) noexcept;
bool mmimage$cxxbridge1$Vec2F32$operator$le(Vec2F32 const &, Vec2F32 const &) noexcept;
bool mmimage$cxxbridge1$Vec2F32$operator$gt(Vec2F32 const &, Vec2F32 const &) noexcept;
bool mmimage$cxxbridge1$Vec2F32$operator$ge(Vec2F32 const &, Vec2F32 const &) noexcept;
bool mmimage$cxxbridge1$Vec2I32$operator$eq(Vec2I32 const &, Vec2I32 const &) noexcept;
bool mmimage$cxxbridge1$Vec2I32$operator$lt(Vec2I32 const &, Vec2I32 const &) noexcept;
bool mmimage$cxxbridge1$Vec2I32$operator$le(Vec2I32 const &, Vec2I32 const &) noexcept;
::std::size_t mmimage$cxxbridge1$Vec2I32$operator$hash(Vec2I32 const &) noexcept;
bool mmimage$cxxbridge1$Box2F32$operator$eq(Box2F32 const &, Box2F32 const &) noexcept;
bool mmimage$cxxbridge1$Box2F32$operator$ne(Box2F32 const &, Box2F32 const &) noexcept;
bool mmimage$cxxbridge1$Box2F32$operator$lt(Box2F32 const &, Box2F32 const &) noexcept;
bool mmimage$cxxbridge1$Box2F32$operator$le(Box2F32 const &, Box2F32 const &) noexcept;
bool mmimage$cxxbridge1$Box2F32$operator$gt(Box2F32 const &, Box2F32 const &) noexcept;
bool mmimage$cxxbridge1$Box2F32$operator$ge(Box2F32 const &, Box2F32 const &) noexcept;
bool mmimage$cxxbridge1$ImageRegionRectangle$operator$eq(ImageRegionRectangle const &, ImageRegionRectangle const &) noexcept;
bool mmimage$cxxbridge1$ImageRegionRectangle$operator$lt(ImageRegionRectangle const &, ImageRegionRectangle const &) noexcept;
bool mmimage$cxxbridge1$ImageRegionRectangle$operator$le(ImageRegionRectangle const &, ImageRegionRectangle const &) noexcept;
::std::size_t mmimage$cxxbridge1$ImageRegionRectangle$operator$hash(ImageRegionRectangle const &) noexcept;
bool mmimage$cxxbridge1$PixelF32x4$operator$eq(PixelF32x4 const &, PixelF32x4 const &) noexcept;
bool mmimage$cxxbridge1$PixelF32x4$operator$ne(PixelF32x4 const &, PixelF32x4 const &) noexcept;
bool mmimage$cxxbridge1$PixelF32x4$operator$lt(PixelF32x4 const &, PixelF32x4 const &) noexcept;
bool mmimage$cxxbridge1$PixelF32x4$operator$le(PixelF32x4 const &, PixelF32x4 const &) noexcept;
bool mmimage$cxxbridge1$PixelF32x4$operator$gt(PixelF32x4 const &, PixelF32x4 const &) noexcept;
bool mmimage$cxxbridge1$PixelF32x4$operator$ge(PixelF32x4 const &, PixelF32x4 const &) noexcept;
bool mmimage$cxxbridge1$PixelF64x2$operator$eq(PixelF64x2 const &, PixelF64x2 const &) noexcept;
bool mmimage$cxxbridge1$PixelF64x2$operator$ne(PixelF64x2 const &, PixelF64x2 const &) noexcept;
bool mmimage$cxxbridge1$PixelF64x2$operator$lt(PixelF64x2 const &, PixelF64x2 const &) noexcept;
bool mmimage$cxxbridge1$PixelF64x2$operator$le(PixelF64x2 const &, PixelF64x2 const &) noexcept;
bool mmimage$cxxbridge1$PixelF64x2$operator$gt(PixelF64x2 const &, PixelF64x2 const &) noexcept;
bool mmimage$cxxbridge1$PixelF64x2$operator$ge(PixelF64x2 const &, PixelF64x2 const &) noexcept;
::std::size_t mmimage$cxxbridge1$ShimImagePixelBuffer$operator$sizeof() noexcept;
::std::size_t mmimage$cxxbridge1$ShimImagePixelBuffer$operator$alignof() noexcept;

::mmimage::BufferDataType mmimage$cxxbridge1$ShimImagePixelBuffer$data_type(::mmimage::ShimImagePixelBuffer const &self) noexcept;

::std::size_t mmimage$cxxbridge1$ShimImagePixelBuffer$image_width(::mmimage::ShimImagePixelBuffer const &self) noexcept;

::std::size_t mmimage$cxxbridge1$ShimImagePixelBuffer$image_height(::mmimage::ShimImagePixelBuffer const &self) noexcept;

::std::size_t mmimage$cxxbridge1$ShimImagePixelBuffer$num_channels(::mmimage::ShimImagePixelBuffer const &self) noexcept;

::std::size_t mmimage$cxxbridge1$ShimImagePixelBuffer$pixel_count(::mmimage::ShimImagePixelBuffer const &self) noexcept;

::std::size_t mmimage$cxxbridge1$ShimImagePixelBuffer$element_count(::mmimage::ShimImagePixelBuffer const &self) noexcept;

::rust::repr::Fat mmimage$cxxbridge1$ShimImagePixelBuffer$as_slice_f32x4(::mmimage::ShimImagePixelBuffer const &self) noexcept;

::rust::repr::Fat mmimage$cxxbridge1$ShimImagePixelBuffer$as_slice_f32x4_mut(::mmimage::ShimImagePixelBuffer &self) noexcept;

void mmimage$cxxbridge1$ShimImagePixelBuffer$resize(::mmimage::ShimImagePixelBuffer &self, ::mmimage::BufferDataType data_type, ::std::size_t image_width, ::std::size_t image_height, ::std::size_t num_channels) noexcept;

::mmimage::ShimImagePixelBuffer *mmimage$cxxbridge1$shim_create_image_pixel_buffer_box() noexcept;
::std::size_t mmimage$cxxbridge1$ShimImageMetaData$operator$sizeof() noexcept;
::std::size_t mmimage$cxxbridge1$ShimImageMetaData$operator$alignof() noexcept;

::mmimage::ImageRegionRectangle mmimage$cxxbridge1$ShimImageMetaData$get_display_window(::mmimage::ShimImageMetaData const &self) noexcept;

void mmimage$cxxbridge1$ShimImageMetaData$set_display_window(::mmimage::ShimImageMetaData &self, ::mmimage::ImageRegionRectangle value) noexcept;

float mmimage$cxxbridge1$ShimImageMetaData$get_pixel_aspect(::mmimage::ShimImageMetaData const &self) noexcept;

void mmimage$cxxbridge1$ShimImageMetaData$set_pixel_aspect(::mmimage::ShimImageMetaData &self, float value) noexcept;

::rust::repr::Fat mmimage$cxxbridge1$ShimImageMetaData$get_layer_name(::mmimage::ShimImageMetaData const &self) noexcept;

void mmimage$cxxbridge1$ShimImageMetaData$set_layer_name(::mmimage::ShimImageMetaData &self, ::rust::Str value) noexcept;

::mmimage::Vec2I32 mmimage$cxxbridge1$ShimImageMetaData$get_layer_position(::mmimage::ShimImageMetaData const &self) noexcept;

void mmimage$cxxbridge1$ShimImageMetaData$set_layer_position(::mmimage::ShimImageMetaData &self, ::mmimage::Vec2I32 value) noexcept;

::mmimage::Vec2F32 mmimage$cxxbridge1$ShimImageMetaData$get_screen_window_center(::mmimage::ShimImageMetaData const &self) noexcept;

void mmimage$cxxbridge1$ShimImageMetaData$set_screen_window_center(::mmimage::ShimImageMetaData &self, ::mmimage::Vec2F32 value) noexcept;

float mmimage$cxxbridge1$ShimImageMetaData$get_screen_window_width(::mmimage::ShimImageMetaData const &self) noexcept;

void mmimage$cxxbridge1$ShimImageMetaData$set_screen_window_width(::mmimage::ShimImageMetaData &self, float value) noexcept;

::rust::repr::Fat mmimage$cxxbridge1$ShimImageMetaData$get_owner(::mmimage::ShimImageMetaData const &self) noexcept;

void mmimage$cxxbridge1$ShimImageMetaData$set_owner(::mmimage::ShimImageMetaData &self, ::rust::Str value) noexcept;

::rust::repr::Fat mmimage$cxxbridge1$ShimImageMetaData$get_comments(::mmimage::ShimImageMetaData const &self) noexcept;

void mmimage$cxxbridge1$ShimImageMetaData$set_comments(::mmimage::ShimImageMetaData &self, ::rust::Str value) noexcept;

::rust::repr::Fat mmimage$cxxbridge1$ShimImageMetaData$get_capture_date(::mmimage::ShimImageMetaData const &self) noexcept;

::mmimage::OptionF32 mmimage$cxxbridge1$ShimImageMetaData$get_utc_offset(::mmimage::ShimImageMetaData const &self) noexcept;

::mmimage::OptionF32 mmimage$cxxbridge1$ShimImageMetaData$get_longitude(::mmimage::ShimImageMetaData const &self) noexcept;

::mmimage::OptionF32 mmimage$cxxbridge1$ShimImageMetaData$get_latitude(::mmimage::ShimImageMetaData const &self) noexcept;

::mmimage::OptionF32 mmimage$cxxbridge1$ShimImageMetaData$get_altitude(::mmimage::ShimImageMetaData const &self) noexcept;

::mmimage::OptionF32 mmimage$cxxbridge1$ShimImageMetaData$get_focus(::mmimage::ShimImageMetaData const &self) noexcept;

::mmimage::OptionF32 mmimage$cxxbridge1$ShimImageMetaData$get_exposure(::mmimage::ShimImageMetaData const &self) noexcept;

::mmimage::OptionF32 mmimage$cxxbridge1$ShimImageMetaData$get_aperture(::mmimage::ShimImageMetaData const &self) noexcept;

::mmimage::OptionF32 mmimage$cxxbridge1$ShimImageMetaData$get_iso_speed(::mmimage::ShimImageMetaData const &self) noexcept;

::mmimage::OptionF32 mmimage$cxxbridge1$ShimImageMetaData$get_frames_per_second(::mmimage::ShimImageMetaData const &self) noexcept;

::rust::repr::Fat mmimage$cxxbridge1$ShimImageMetaData$get_software_name(::mmimage::ShimImageMetaData const &self) noexcept;

void mmimage$cxxbridge1$ShimImageMetaData$set_software_name(::mmimage::ShimImageMetaData &self, ::rust::Str value) noexcept;

void mmimage$cxxbridge1$ShimImageMetaData$all_named_attribute_names(::mmimage::ShimImageMetaData const &self, ::rust::Vec<::rust::String> *return$) noexcept;

bool mmimage$cxxbridge1$ShimImageMetaData$has_named_attribute(::mmimage::ShimImageMetaData const &self, ::rust::Str attribute_name) noexcept;

::std::uint8_t mmimage$cxxbridge1$ShimImageMetaData$get_named_attribute_type_index(::mmimage::ShimImageMetaData const &self, ::rust::Str attribute_name) noexcept;

::std::int32_t mmimage$cxxbridge1$ShimImageMetaData$get_named_attribute_as_i32(::mmimage::ShimImageMetaData const &self, ::rust::Str attribute_name) noexcept;

float mmimage$cxxbridge1$ShimImageMetaData$get_named_attribute_as_f32(::mmimage::ShimImageMetaData const &self, ::rust::Str attribute_name) noexcept;

double mmimage$cxxbridge1$ShimImageMetaData$get_named_attribute_as_f64(::mmimage::ShimImageMetaData const &self, ::rust::Str attribute_name) noexcept;

void mmimage$cxxbridge1$ShimImageMetaData$get_named_attribute_as_string(::mmimage::ShimImageMetaData const &self, ::rust::Str attribute_name, ::rust::String *return$) noexcept;

void mmimage$cxxbridge1$ShimImageMetaData$as_string(::mmimage::ShimImageMetaData const &self, ::rust::String *return$) noexcept;

::mmimage::ShimImageMetaData *mmimage$cxxbridge1$shim_create_image_meta_data_box() noexcept;

bool mmimage$cxxbridge1$shim_image_read_pixels_exr_f32x4(::rust::Str file_path, bool vertical_flip, ::rust::Box<::mmimage::ShimImageMetaData> &out_meta_data, ::rust::Box<::mmimage::ShimImagePixelBuffer> &out_pixel_buffer) noexcept;

bool mmimage$cxxbridge1$shim_image_read_metadata_exr(::rust::Str file_path, ::rust::Box<::mmimage::ShimImageMetaData> &out_meta_data) noexcept;

bool mmimage$cxxbridge1$shim_image_write_pixels_exr_f32x4(::rust::Str file_path, ::mmimage::ImageExrEncoder exr_encoder, ::rust::Box<::mmimage::ShimImageMetaData> const &in_meta_data, ::rust::Box<::mmimage::ShimImagePixelBuffer> const &in_pixel_buffer) noexcept;
} // extern "C"
} // namespace mmimage

namespace std {
template <> struct hash<::mmimage::Vec2I32> {
  ::std::size_t operator()(::mmimage::Vec2I32 const &self) const noexcept {
    return ::mmimage::mmimage$cxxbridge1$Vec2I32$operator$hash(self);
  }
};

template <> struct hash<::mmimage::ImageRegionRectangle> {
  ::std::size_t operator()(::mmimage::ImageRegionRectangle const &self) const noexcept {
    return ::mmimage::mmimage$cxxbridge1$ImageRegionRectangle$operator$hash(self);
  }
};
} // namespace std

namespace mmimage {
bool ExrPixelLayout::operator==(ExrPixelLayout const &rhs) const noexcept {
  return mmimage$cxxbridge1$ExrPixelLayout$operator$eq(*this, rhs);
}

bool ExrPixelLayout::operator!=(ExrPixelLayout const &rhs) const noexcept {
  return mmimage$cxxbridge1$ExrPixelLayout$operator$ne(*this, rhs);
}

bool ExrPixelLayout::operator<(ExrPixelLayout const &rhs) const noexcept {
  return mmimage$cxxbridge1$ExrPixelLayout$operator$lt(*this, rhs);
}

bool ExrPixelLayout::operator<=(ExrPixelLayout const &rhs) const noexcept {
  return mmimage$cxxbridge1$ExrPixelLayout$operator$le(*this, rhs);
}

bool ExrPixelLayout::operator>(ExrPixelLayout const &rhs) const noexcept {
  return mmimage$cxxbridge1$ExrPixelLayout$operator$gt(*this, rhs);
}

bool ExrPixelLayout::operator>=(ExrPixelLayout const &rhs) const noexcept {
  return mmimage$cxxbridge1$ExrPixelLayout$operator$ge(*this, rhs);
}

bool ImageExrEncoder::operator==(ImageExrEncoder const &rhs) const noexcept {
  return mmimage$cxxbridge1$ImageExrEncoder$operator$eq(*this, rhs);
}

bool ImageExrEncoder::operator!=(ImageExrEncoder const &rhs) const noexcept {
  return mmimage$cxxbridge1$ImageExrEncoder$operator$ne(*this, rhs);
}

bool ImageExrEncoder::operator<(ImageExrEncoder const &rhs) const noexcept {
  return mmimage$cxxbridge1$ImageExrEncoder$operator$lt(*this, rhs);
}

bool ImageExrEncoder::operator<=(ImageExrEncoder const &rhs) const noexcept {
  return mmimage$cxxbridge1$ImageExrEncoder$operator$le(*this, rhs);
}

bool ImageExrEncoder::operator>(ImageExrEncoder const &rhs) const noexcept {
  return mmimage$cxxbridge1$ImageExrEncoder$operator$gt(*this, rhs);
}

bool ImageExrEncoder::operator>=(ImageExrEncoder const &rhs) const noexcept {
  return mmimage$cxxbridge1$ImageExrEncoder$operator$ge(*this, rhs);
}

bool OptionF32::operator==(OptionF32 const &rhs) const noexcept {
  return mmimage$cxxbridge1$OptionF32$operator$eq(*this, rhs);
}

bool OptionF32::operator!=(OptionF32 const &rhs) const noexcept {
  return mmimage$cxxbridge1$OptionF32$operator$ne(*this, rhs);
}

bool OptionF32::operator<(OptionF32 const &rhs) const noexcept {
  return mmimage$cxxbridge1$OptionF32$operator$lt(*this, rhs);
}

bool OptionF32::operator<=(OptionF32 const &rhs) const noexcept {
  return mmimage$cxxbridge1$OptionF32$operator$le(*this, rhs);
}

bool OptionF32::operator>(OptionF32 const &rhs) const noexcept {
  return mmimage$cxxbridge1$OptionF32$operator$gt(*this, rhs);
}

bool OptionF32::operator>=(OptionF32 const &rhs) const noexcept {
  return mmimage$cxxbridge1$OptionF32$operator$ge(*this, rhs);
}

bool Vec2F32::operator==(Vec2F32 const &rhs) const noexcept {
  return mmimage$cxxbridge1$Vec2F32$operator$eq(*this, rhs);
}

bool Vec2F32::operator!=(Vec2F32 const &rhs) const noexcept {
  return mmimage$cxxbridge1$Vec2F32$operator$ne(*this, rhs);
}

bool Vec2F32::operator<(Vec2F32 const &rhs) const noexcept {
  return mmimage$cxxbridge1$Vec2F32$operator$lt(*this, rhs);
}

bool Vec2F32::operator<=(Vec2F32 const &rhs) const noexcept {
  return mmimage$cxxbridge1$Vec2F32$operator$le(*this, rhs);
}

bool Vec2F32::operator>(Vec2F32 const &rhs) const noexcept {
  return mmimage$cxxbridge1$Vec2F32$operator$gt(*this, rhs);
}

bool Vec2F32::operator>=(Vec2F32 const &rhs) const noexcept {
  return mmimage$cxxbridge1$Vec2F32$operator$ge(*this, rhs);
}

bool Vec2I32::operator==(Vec2I32 const &rhs) const noexcept {
  return mmimage$cxxbridge1$Vec2I32$operator$eq(*this, rhs);
}

bool Vec2I32::operator!=(Vec2I32 const &rhs) const noexcept {
  return !(*this == rhs);
}

bool Vec2I32::operator<(Vec2I32 const &rhs) const noexcept {
  return mmimage$cxxbridge1$Vec2I32$operator$lt(*this, rhs);
}

bool Vec2I32::operator<=(Vec2I32 const &rhs) const noexcept {
  return mmimage$cxxbridge1$Vec2I32$operator$le(*this, rhs);
}

bool Vec2I32::operator>(Vec2I32 const &rhs) const noexcept {
  return !(*this <= rhs);
}

bool Vec2I32::operator>=(Vec2I32 const &rhs) const noexcept {
  return !(*this < rhs);
}

bool Box2F32::operator==(Box2F32 const &rhs) const noexcept {
  return mmimage$cxxbridge1$Box2F32$operator$eq(*this, rhs);
}

bool Box2F32::operator!=(Box2F32 const &rhs) const noexcept {
  return mmimage$cxxbridge1$Box2F32$operator$ne(*this, rhs);
}

bool Box2F32::operator<(Box2F32 const &rhs) const noexcept {
  return mmimage$cxxbridge1$Box2F32$operator$lt(*this, rhs);
}

bool Box2F32::operator<=(Box2F32 const &rhs) const noexcept {
  return mmimage$cxxbridge1$Box2F32$operator$le(*this, rhs);
}

bool Box2F32::operator>(Box2F32 const &rhs) const noexcept {
  return mmimage$cxxbridge1$Box2F32$operator$gt(*this, rhs);
}

bool Box2F32::operator>=(Box2F32 const &rhs) const noexcept {
  return mmimage$cxxbridge1$Box2F32$operator$ge(*this, rhs);
}

bool ImageRegionRectangle::operator==(ImageRegionRectangle const &rhs) const noexcept {
  return mmimage$cxxbridge1$ImageRegionRectangle$operator$eq(*this, rhs);
}

bool ImageRegionRectangle::operator!=(ImageRegionRectangle const &rhs) const noexcept {
  return !(*this == rhs);
}

bool ImageRegionRectangle::operator<(ImageRegionRectangle const &rhs) const noexcept {
  return mmimage$cxxbridge1$ImageRegionRectangle$operator$lt(*this, rhs);
}

bool ImageRegionRectangle::operator<=(ImageRegionRectangle const &rhs) const noexcept {
  return mmimage$cxxbridge1$ImageRegionRectangle$operator$le(*this, rhs);
}

bool ImageRegionRectangle::operator>(ImageRegionRectangle const &rhs) const noexcept {
  return !(*this <= rhs);
}

bool ImageRegionRectangle::operator>=(ImageRegionRectangle const &rhs) const noexcept {
  return !(*this < rhs);
}

bool PixelF32x4::operator==(PixelF32x4 const &rhs) const noexcept {
  return mmimage$cxxbridge1$PixelF32x4$operator$eq(*this, rhs);
}

bool PixelF32x4::operator!=(PixelF32x4 const &rhs) const noexcept {
  return mmimage$cxxbridge1$PixelF32x4$operator$ne(*this, rhs);
}

bool PixelF32x4::operator<(PixelF32x4 const &rhs) const noexcept {
  return mmimage$cxxbridge1$PixelF32x4$operator$lt(*this, rhs);
}

bool PixelF32x4::operator<=(PixelF32x4 const &rhs) const noexcept {
  return mmimage$cxxbridge1$PixelF32x4$operator$le(*this, rhs);
}

bool PixelF32x4::operator>(PixelF32x4 const &rhs) const noexcept {
  return mmimage$cxxbridge1$PixelF32x4$operator$gt(*this, rhs);
}

bool PixelF32x4::operator>=(PixelF32x4 const &rhs) const noexcept {
  return mmimage$cxxbridge1$PixelF32x4$operator$ge(*this, rhs);
}

bool PixelF64x2::operator==(PixelF64x2 const &rhs) const noexcept {
  return mmimage$cxxbridge1$PixelF64x2$operator$eq(*this, rhs);
}

bool PixelF64x2::operator!=(PixelF64x2 const &rhs) const noexcept {
  return mmimage$cxxbridge1$PixelF64x2$operator$ne(*this, rhs);
}

bool PixelF64x2::operator<(PixelF64x2 const &rhs) const noexcept {
  return mmimage$cxxbridge1$PixelF64x2$operator$lt(*this, rhs);
}

bool PixelF64x2::operator<=(PixelF64x2 const &rhs) const noexcept {
  return mmimage$cxxbridge1$PixelF64x2$operator$le(*this, rhs);
}

bool PixelF64x2::operator>(PixelF64x2 const &rhs) const noexcept {
  return mmimage$cxxbridge1$PixelF64x2$operator$gt(*this, rhs);
}

bool PixelF64x2::operator>=(PixelF64x2 const &rhs) const noexcept {
  return mmimage$cxxbridge1$PixelF64x2$operator$ge(*this, rhs);
}

::std::size_t ShimImagePixelBuffer::layout::size() noexcept {
  return mmimage$cxxbridge1$ShimImagePixelBuffer$operator$sizeof();
}

::std::size_t ShimImagePixelBuffer::layout::align() noexcept {
  return mmimage$cxxbridge1$ShimImagePixelBuffer$operator$alignof();
}

MMIMAGE_API_EXPORT ::mmimage::BufferDataType ShimImagePixelBuffer::data_type() const noexcept {
  return mmimage$cxxbridge1$ShimImagePixelBuffer$data_type(*this);
}

MMIMAGE_API_EXPORT ::std::size_t ShimImagePixelBuffer::image_width() const noexcept {
  return mmimage$cxxbridge1$ShimImagePixelBuffer$image_width(*this);
}

MMIMAGE_API_EXPORT ::std::size_t ShimImagePixelBuffer::image_height() const noexcept {
  return mmimage$cxxbridge1$ShimImagePixelBuffer$image_height(*this);
}

MMIMAGE_API_EXPORT ::std::size_t ShimImagePixelBuffer::num_channels() const noexcept {
  return mmimage$cxxbridge1$ShimImagePixelBuffer$num_channels(*this);
}

MMIMAGE_API_EXPORT ::std::size_t ShimImagePixelBuffer::pixel_count() const noexcept {
  return mmimage$cxxbridge1$ShimImagePixelBuffer$pixel_count(*this);
}

MMIMAGE_API_EXPORT ::std::size_t ShimImagePixelBuffer::element_count() const noexcept {
  return mmimage$cxxbridge1$ShimImagePixelBuffer$element_count(*this);
}

MMIMAGE_API_EXPORT ::rust::Slice<::mmimage::PixelF32x4 const> ShimImagePixelBuffer::as_slice_f32x4() const noexcept {
  return ::rust::impl<::rust::Slice<::mmimage::PixelF32x4 const>>::slice(mmimage$cxxbridge1$ShimImagePixelBuffer$as_slice_f32x4(*this));
}

MMIMAGE_API_EXPORT ::rust::Slice<::mmimage::PixelF32x4 > ShimImagePixelBuffer::as_slice_f32x4_mut() noexcept {
  return ::rust::impl<::rust::Slice<::mmimage::PixelF32x4 >>::slice(mmimage$cxxbridge1$ShimImagePixelBuffer$as_slice_f32x4_mut(*this));
}

MMIMAGE_API_EXPORT void ShimImagePixelBuffer::resize(::mmimage::BufferDataType data_type, ::std::size_t image_width, ::std::size_t image_height, ::std::size_t num_channels) noexcept {
  mmimage$cxxbridge1$ShimImagePixelBuffer$resize(*this, data_type, image_width, image_height, num_channels);
}

MMIMAGE_API_EXPORT ::rust::Box<::mmimage::ShimImagePixelBuffer> shim_create_image_pixel_buffer_box() noexcept {
  return ::rust::Box<::mmimage::ShimImagePixelBuffer>::from_raw(mmimage$cxxbridge1$shim_create_image_pixel_buffer_box());
}

::std::size_t ShimImageMetaData::layout::size() noexcept {
  return mmimage$cxxbridge1$ShimImageMetaData$operator$sizeof();
}

::std::size_t ShimImageMetaData::layout::align() noexcept {
  return mmimage$cxxbridge1$ShimImageMetaData$operator$alignof();
}

MMIMAGE_API_EXPORT ::mmimage::ImageRegionRectangle ShimImageMetaData::get_display_window() const noexcept {
  return mmimage$cxxbridge1$ShimImageMetaData$get_display_window(*this);
}

MMIMAGE_API_EXPORT void ShimImageMetaData::set_display_window(::mmimage::ImageRegionRectangle value) noexcept {
  mmimage$cxxbridge1$ShimImageMetaData$set_display_window(*this, value);
}

MMIMAGE_API_EXPORT float ShimImageMetaData::get_pixel_aspect() const noexcept {
  return mmimage$cxxbridge1$ShimImageMetaData$get_pixel_aspect(*this);
}

MMIMAGE_API_EXPORT void ShimImageMetaData::set_pixel_aspect(float value) noexcept {
  mmimage$cxxbridge1$ShimImageMetaData$set_pixel_aspect(*this, value);
}

MMIMAGE_API_EXPORT ::rust::Str ShimImageMetaData::get_layer_name() const noexcept {
  return ::rust::impl<::rust::Str>::new_unchecked(mmimage$cxxbridge1$ShimImageMetaData$get_layer_name(*this));
}

MMIMAGE_API_EXPORT void ShimImageMetaData::set_layer_name(::rust::Str value) noexcept {
  mmimage$cxxbridge1$ShimImageMetaData$set_layer_name(*this, value);
}

MMIMAGE_API_EXPORT ::mmimage::Vec2I32 ShimImageMetaData::get_layer_position() const noexcept {
  return mmimage$cxxbridge1$ShimImageMetaData$get_layer_position(*this);
}

MMIMAGE_API_EXPORT void ShimImageMetaData::set_layer_position(::mmimage::Vec2I32 value) noexcept {
  mmimage$cxxbridge1$ShimImageMetaData$set_layer_position(*this, value);
}

MMIMAGE_API_EXPORT ::mmimage::Vec2F32 ShimImageMetaData::get_screen_window_center() const noexcept {
  return mmimage$cxxbridge1$ShimImageMetaData$get_screen_window_center(*this);
}

MMIMAGE_API_EXPORT void ShimImageMetaData::set_screen_window_center(::mmimage::Vec2F32 value) noexcept {
  mmimage$cxxbridge1$ShimImageMetaData$set_screen_window_center(*this, value);
}

MMIMAGE_API_EXPORT float ShimImageMetaData::get_screen_window_width() const noexcept {
  return mmimage$cxxbridge1$ShimImageMetaData$get_screen_window_width(*this);
}

MMIMAGE_API_EXPORT void ShimImageMetaData::set_screen_window_width(float value) noexcept {
  mmimage$cxxbridge1$ShimImageMetaData$set_screen_window_width(*this, value);
}

MMIMAGE_API_EXPORT ::rust::Str ShimImageMetaData::get_owner() const noexcept {
  return ::rust::impl<::rust::Str>::new_unchecked(mmimage$cxxbridge1$ShimImageMetaData$get_owner(*this));
}

MMIMAGE_API_EXPORT void ShimImageMetaData::set_owner(::rust::Str value) noexcept {
  mmimage$cxxbridge1$ShimImageMetaData$set_owner(*this, value);
}

MMIMAGE_API_EXPORT ::rust::Str ShimImageMetaData::get_comments() const noexcept {
  return ::rust::impl<::rust::Str>::new_unchecked(mmimage$cxxbridge1$ShimImageMetaData$get_comments(*this));
}

MMIMAGE_API_EXPORT void ShimImageMetaData::set_comments(::rust::Str value) noexcept {
  mmimage$cxxbridge1$ShimImageMetaData$set_comments(*this, value);
}

MMIMAGE_API_EXPORT ::rust::Str ShimImageMetaData::get_capture_date() const noexcept {
  return ::rust::impl<::rust::Str>::new_unchecked(mmimage$cxxbridge1$ShimImageMetaData$get_capture_date(*this));
}

MMIMAGE_API_EXPORT ::mmimage::OptionF32 ShimImageMetaData::get_utc_offset() const noexcept {
  return mmimage$cxxbridge1$ShimImageMetaData$get_utc_offset(*this);
}

MMIMAGE_API_EXPORT ::mmimage::OptionF32 ShimImageMetaData::get_longitude() const noexcept {
  return mmimage$cxxbridge1$ShimImageMetaData$get_longitude(*this);
}

MMIMAGE_API_EXPORT ::mmimage::OptionF32 ShimImageMetaData::get_latitude() const noexcept {
  return mmimage$cxxbridge1$ShimImageMetaData$get_latitude(*this);
}

MMIMAGE_API_EXPORT ::mmimage::OptionF32 ShimImageMetaData::get_altitude() const noexcept {
  return mmimage$cxxbridge1$ShimImageMetaData$get_altitude(*this);
}

MMIMAGE_API_EXPORT ::mmimage::OptionF32 ShimImageMetaData::get_focus() const noexcept {
  return mmimage$cxxbridge1$ShimImageMetaData$get_focus(*this);
}

MMIMAGE_API_EXPORT ::mmimage::OptionF32 ShimImageMetaData::get_exposure() const noexcept {
  return mmimage$cxxbridge1$ShimImageMetaData$get_exposure(*this);
}

MMIMAGE_API_EXPORT ::mmimage::OptionF32 ShimImageMetaData::get_aperture() const noexcept {
  return mmimage$cxxbridge1$ShimImageMetaData$get_aperture(*this);
}

MMIMAGE_API_EXPORT ::mmimage::OptionF32 ShimImageMetaData::get_iso_speed() const noexcept {
  return mmimage$cxxbridge1$ShimImageMetaData$get_iso_speed(*this);
}

MMIMAGE_API_EXPORT ::mmimage::OptionF32 ShimImageMetaData::get_frames_per_second() const noexcept {
  return mmimage$cxxbridge1$ShimImageMetaData$get_frames_per_second(*this);
}

MMIMAGE_API_EXPORT ::rust::Str ShimImageMetaData::get_software_name() const noexcept {
  return ::rust::impl<::rust::Str>::new_unchecked(mmimage$cxxbridge1$ShimImageMetaData$get_software_name(*this));
}

MMIMAGE_API_EXPORT void ShimImageMetaData::set_software_name(::rust::Str value) noexcept {
  mmimage$cxxbridge1$ShimImageMetaData$set_software_name(*this, value);
}

MMIMAGE_API_EXPORT ::rust::Vec<::rust::String> ShimImageMetaData::all_named_attribute_names() const noexcept {
  ::rust::MaybeUninit<::rust::Vec<::rust::String>> return$;
  mmimage$cxxbridge1$ShimImageMetaData$all_named_attribute_names(*this, &return$.value);
  return ::std::move(return$.value);
}

MMIMAGE_API_EXPORT bool ShimImageMetaData::has_named_attribute(::rust::Str attribute_name) const noexcept {
  return mmimage$cxxbridge1$ShimImageMetaData$has_named_attribute(*this, attribute_name);
}

MMIMAGE_API_EXPORT ::std::uint8_t ShimImageMetaData::get_named_attribute_type_index(::rust::Str attribute_name) const noexcept {
  return mmimage$cxxbridge1$ShimImageMetaData$get_named_attribute_type_index(*this, attribute_name);
}

MMIMAGE_API_EXPORT ::std::int32_t ShimImageMetaData::get_named_attribute_as_i32(::rust::Str attribute_name) const noexcept {
  return mmimage$cxxbridge1$ShimImageMetaData$get_named_attribute_as_i32(*this, attribute_name);
}

MMIMAGE_API_EXPORT float ShimImageMetaData::get_named_attribute_as_f32(::rust::Str attribute_name) const noexcept {
  return mmimage$cxxbridge1$ShimImageMetaData$get_named_attribute_as_f32(*this, attribute_name);
}

MMIMAGE_API_EXPORT double ShimImageMetaData::get_named_attribute_as_f64(::rust::Str attribute_name) const noexcept {
  return mmimage$cxxbridge1$ShimImageMetaData$get_named_attribute_as_f64(*this, attribute_name);
}

MMIMAGE_API_EXPORT ::rust::String ShimImageMetaData::get_named_attribute_as_string(::rust::Str attribute_name) const noexcept {
  ::rust::MaybeUninit<::rust::String> return$;
  mmimage$cxxbridge1$ShimImageMetaData$get_named_attribute_as_string(*this, attribute_name, &return$.value);
  return ::std::move(return$.value);
}

MMIMAGE_API_EXPORT ::rust::String ShimImageMetaData::as_string() const noexcept {
  ::rust::MaybeUninit<::rust::String> return$;
  mmimage$cxxbridge1$ShimImageMetaData$as_string(*this, &return$.value);
  return ::std::move(return$.value);
}

MMIMAGE_API_EXPORT ::rust::Box<::mmimage::ShimImageMetaData> shim_create_image_meta_data_box() noexcept {
  return ::rust::Box<::mmimage::ShimImageMetaData>::from_raw(mmimage$cxxbridge1$shim_create_image_meta_data_box());
}

MMIMAGE_API_EXPORT bool shim_image_read_pixels_exr_f32x4(::rust::Str file_path, bool vertical_flip, ::rust::Box<::mmimage::ShimImageMetaData> &out_meta_data, ::rust::Box<::mmimage::ShimImagePixelBuffer> &out_pixel_buffer) noexcept {
  return mmimage$cxxbridge1$shim_image_read_pixels_exr_f32x4(file_path, vertical_flip, out_meta_data, out_pixel_buffer);
}

MMIMAGE_API_EXPORT bool shim_image_read_metadata_exr(::rust::Str file_path, ::rust::Box<::mmimage::ShimImageMetaData> &out_meta_data) noexcept {
  return mmimage$cxxbridge1$shim_image_read_metadata_exr(file_path, out_meta_data);
}

MMIMAGE_API_EXPORT bool shim_image_write_pixels_exr_f32x4(::rust::Str file_path, ::mmimage::ImageExrEncoder exr_encoder, ::rust::Box<::mmimage::ShimImageMetaData> const &in_meta_data, ::rust::Box<::mmimage::ShimImagePixelBuffer> const &in_pixel_buffer) noexcept {
  return mmimage$cxxbridge1$shim_image_write_pixels_exr_f32x4(file_path, exr_encoder, in_meta_data, in_pixel_buffer);
}
} // namespace mmimage

extern "C" {
::mmimage::ShimImagePixelBuffer *cxxbridge1$box$mmimage$ShimImagePixelBuffer$alloc() noexcept;
void cxxbridge1$box$mmimage$ShimImagePixelBuffer$dealloc(::mmimage::ShimImagePixelBuffer *) noexcept;
void cxxbridge1$box$mmimage$ShimImagePixelBuffer$drop(::rust::Box<::mmimage::ShimImagePixelBuffer> *ptr) noexcept;

::mmimage::ShimImageMetaData *cxxbridge1$box$mmimage$ShimImageMetaData$alloc() noexcept;
void cxxbridge1$box$mmimage$ShimImageMetaData$dealloc(::mmimage::ShimImageMetaData *) noexcept;
void cxxbridge1$box$mmimage$ShimImageMetaData$drop(::rust::Box<::mmimage::ShimImageMetaData> *ptr) noexcept;
} // extern "C"

namespace rust {
inline namespace cxxbridge1 {
template <>
MMIMAGE_API_EXPORT ::mmimage::ShimImagePixelBuffer *Box<::mmimage::ShimImagePixelBuffer>::allocation::alloc() noexcept {
  return cxxbridge1$box$mmimage$ShimImagePixelBuffer$alloc();
}
template <>
MMIMAGE_API_EXPORT void Box<::mmimage::ShimImagePixelBuffer>::allocation::dealloc(::mmimage::ShimImagePixelBuffer *ptr) noexcept {
  cxxbridge1$box$mmimage$ShimImagePixelBuffer$dealloc(ptr);
}
template <>
MMIMAGE_API_EXPORT void Box<::mmimage::ShimImagePixelBuffer>::drop() noexcept {
  cxxbridge1$box$mmimage$ShimImagePixelBuffer$drop(this);
}
template <>
MMIMAGE_API_EXPORT ::mmimage::ShimImageMetaData *Box<::mmimage::ShimImageMetaData>::allocation::alloc() noexcept {
  return cxxbridge1$box$mmimage$ShimImageMetaData$alloc();
}
template <>
MMIMAGE_API_EXPORT void Box<::mmimage::ShimImageMetaData>::allocation::dealloc(::mmimage::ShimImageMetaData *ptr) noexcept {
  cxxbridge1$box$mmimage$ShimImageMetaData$dealloc(ptr);
}
template <>
MMIMAGE_API_EXPORT void Box<::mmimage::ShimImageMetaData>::drop() noexcept {
  cxxbridge1$box$mmimage$ShimImageMetaData$drop(this);
}
} // namespace cxxbridge1
} // namespace rust
