# OpenMVG Patches

`cmakeFindModules_Find*.cmake` files were changed to force CMake
to skip finding JPEG, PNG and TIFF for internal builds. The intention
is that any installed system libraries are ignored.

`robust_estimator_ACRansac.hpp` has a segfault fixed which occurs on
Linux with GCC 9.3.1 20200408 (Red Hat 9.3.1-2). In `ACRANSAC` the
std::vector `vec_models` was being deallocated per-run of the loop
which seemed caused a segfault - the fix is to pull `vec_models`
outside the loop and reserve the size to avoid reallocation
per-iteration.
