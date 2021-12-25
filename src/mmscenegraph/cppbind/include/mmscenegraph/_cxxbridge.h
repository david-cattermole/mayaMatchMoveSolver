#pragma once
#include "mmscenegraph/_cxx.h"
#include "mmscenegraph/_symbol_export.h"
#include <cstdint>

namespace mmscenegraph {
MMSCENEGRAPH_API_EXPORT void foo(::std::uint32_t number) noexcept;

MMSCENEGRAPH_API_EXPORT ::std::uint32_t foobar(::std::uint32_t number) noexcept;
} // namespace mmscenegraph
