# *****************************************************************************
# Copyright (c) 2016-2020, Intel Corporation
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# - Redistributions of source code must retain the above copyright notice,
#   this list of conditions and the following disclaimer.
# - Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF
# THE POSSIBILITY OF SUCH DAMAGE.
# *****************************************************************************

# The following variables are optionally searched for defaults
#  MATHLIB_ROOT_DIR:     Base directory where all components are found
#
# The following are set after configuration is done:
#  MATHLIB_FOUND
#  MATHLIB_INCLUDE_DIR
#  MATHLIB_LIBRARY_DIR

include(FindPackageHandleStandardArgs)

set(MATHLIB_ROOT_DIR "$ENV{ONEAPI_ROOT}/mkl" CACHE PATH "Folder contains mathlib")
set(MATHLIB_SYCL_LIB ${CMAKE_SHARED_LIBRARY_PREFIX}mkl_sycl_dll${CMAKE_STATIC_LIBRARY_SUFFIX})

find_path(MATHLIB_INCLUDE_DIR oneapi/mkl.hpp
    HINTS ENV CONDA_PREFIX ${MATHLIB_ROOT_DIR}   # search order is important
    PATH_SUFFIXES include latest/include
    DOC "Path to mathlib include files")

find_path(MATHLIB_LIBRARY_DIR ${MATHLIB_SYCL_LIB}
    HINTS ENV CONDA_PREFIX ${MATHLIB_ROOT_DIR}   # search order is important
    PATH_SUFFIXES lib latest/lib/intel64
    DOC "Path to mathlib library files")

# TODO implement recurcive searching
# file(GLOB_RECURSE MY_PATH "/opt/intel/*/mkl.hpp")
# message(STATUS "+++++++++++++: (include: ${MY_PATH})")

find_package_handle_standard_args(MathLib DEFAULT_MSG MATHLIB_INCLUDE_DIR MATHLIB_LIBRARY_DIR)

if(MathLib_FOUND)
    message(STATUS "Found MathLib: (include: ${MATHLIB_INCLUDE_DIR}, library: ${MATHLIB_LIBRARY_DIR})")
    mark_as_advanced(MATHLIB_ROOT_DIR MATHLIB_INCLUDE_DIR MATHLIB_LIBRARY_DIR)
endif()
