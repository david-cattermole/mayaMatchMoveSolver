#include "mmscenegraph/_cxx.h"
#include "mmscenegraph/_symbol_export.h"
#include <cstdint>

namespace mmscenegraph {
extern "C" {
void mmscenegraph$cxxbridge1$foo(::std::uint32_t number) noexcept;

::std::uint32_t mmscenegraph$cxxbridge1$foobar(::std::uint32_t number) noexcept;
} // extern "C"

MMSCENEGRAPH_API_EXPORT void foo(::std::uint32_t number) noexcept {
  mmscenegraph$cxxbridge1$foo(number);
}

MMSCENEGRAPH_API_EXPORT ::std::uint32_t foobar(::std::uint32_t number) noexcept {
  return mmscenegraph$cxxbridge1$foobar(number);
}
} // namespace mmscenegraph
