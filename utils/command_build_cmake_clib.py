# -*- coding: utf-8 -*-
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

"""
Module to call cmake based procedure by build_cmake_clib command
"""

import os
import sys
import pathlib
from setuptools.command import build_clib
from distutils import log


"""
Detect platform
"""
IS_WIN = False
IS_MAC = False
IS_LIN = False

if 'linux' in sys.platform:
    IS_LIN = True
elif sys.platform == 'darwin':
    IS_MAC = True
elif sys.platform in ['win32', 'cygwin']:
    IS_WIN = True
else:
    raise EnvironmentError("DPNP cmake builder: " + sys.platform + " not supported")


"""
Detect external SYCL queue manager
"""
_dpctrl_include_dir = "No_sycl_queue_mgr_include_dir"
_dpctrl_library_dir = "No_sycl_queue_mgr_library_dir"
_dpctrl_exists = "OFF"
try:
    """
    Detect external SYCL queue handling library
    """
    import dpctl

    _dpctrl_include_dir = str(os.path.abspath(dpctl.get_include()))
    _dpctrl_library_dir = str(os.path.abspath(os.path.join(dpctl.get_include(), "..")))
    _dpctrl_exists = "ON"
except ImportError:
    """
    Set local SYCL queue handler set by default in CmakeList.txt
    """
    pass

"""
Detect enabling DPNP backend tests
"""
_dpnp_backend_tests_enable = os.environ.get('DPNP_BACKEND_TESTS_ENABLE', None)


"""
CmakeList.txt based build_clib
"""


class custom_build_cmake_clib(build_clib.build_clib):
    def run(self):
        root_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
        log.info(f"Project directory is: {root_dir}")

        backend_directory = os.path.join(root_dir, "dpnp", "backend")
        install_directory = os.path.join(root_dir, "dpnp")

        build_temp = pathlib.Path(self.build_temp)
        build_temp.mkdir(parents=True, exist_ok=True)
        abs_build_temp_path = str(os.path.abspath(build_temp))
        log.info(f"build directory is: {abs_build_temp_path}")

        config = "Debug" if self.debug else "Release"

        cmake_generator = str()
        enable_tests = "OFF"

        if IS_WIN:
            cmake_generator = "-GNinja"
        if _dpnp_backend_tests_enable is not None:
            enable_tests = "ON"

        cmake_args = [
            cmake_generator,
            "-S" + backend_directory,
            "-B" + abs_build_temp_path,
            "-DCMAKE_BUILD_TYPE=" + config,
            "-DDPNP_INSTALL_PREFIX=" + install_directory.replace(os.sep, "/"),  # adjust to cmake requirenments
            "-DDPNP_INSTALL_STRUCTURED=OFF",
            # "-DCMAKE_LIBRARY_OUTPUT_DIRECTORY=" + install_directory,
            "-DDPNP_SYCL_QUEUE_MGR_ENABLE:BOOL=" + _dpctrl_exists,
            "-DDPNP_QUEUEMGR_INCLUDE_DIR=" + _dpctrl_include_dir,
            "-DDPNP_QUEUEMGR_LIB_DIR=" + _dpctrl_library_dir,
            "-DCMAKE_VERBOSE_MAKEFILE:BOOL=ON",
            "-DDPNP_BACKEND_TESTS:BOOL=" + enable_tests
        ]

        # didn't find how to add it inside cmake, that is why this is here
        import multiprocessing
        cpu_count = multiprocessing.cpu_count()
        # possible that jobs count must be +-1 against CPUs count
        jobs = "-j" + str(cpu_count)

        self.spawn(["cmake"] + cmake_args + [backend_directory])
        if not self.dry_run:
            self.spawn(["cmake", "--build", abs_build_temp_path, jobs])
            self.spawn(["cmake", "--install", abs_build_temp_path])
