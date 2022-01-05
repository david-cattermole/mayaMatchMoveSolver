# define the source files
SET(BASE_SRC aligned_malloc.cc)

# define the header files (make the headers appear in IDEs.)
FILE(GLOB BASE_HDRS *.h)

ADD_LIBRARY(base ${BASE_SRC} ${BASE_HDRS})

# make the name of debug libraries end in _d.
SET_TARGET_PROPERTIES(base PROPERTIES DEBUG_POSTFIX "_d")

# installation rules for the library
LIBMV_INSTALL_LIB(base)

LIBMV_TEST(vector numeric)
LIBMV_TEST(scoped_ptr "")
