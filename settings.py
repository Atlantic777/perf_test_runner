"""
Just raw config data
"""

from os.path import (
    join,
    expanduser,
)

HOME = expanduser("~")
LLVM_BUILD_ROOT = join(HOME, "diplomski/build/llvm")

# SINGLE_SOURCE_TESTS_ROOT = join(LLVM_BUILD_ROOT, "projects/test-suite/SingleSource/Benchmarks/")
SINGLE_SOURCE_TESTS_ROOT = join(HOME, "diplomski/test_sources/")

OUTPUT_ROOT = join(HOME, "diplomski/test_runs/")
TOOLCHAIN_ROOT = join(HOME, "diplomski/toolchains/mips-2013.11")

GCC_PATH = "/usr/bin/gcc"
CROSS_GCC_PATH = join(TOOLCHAIN_ROOT, "bin/mips-linux-gnu-gcc")
CLANG_PATH = join(LLVM_BUILD_ROOT, "build/bin/clang")
OPT_PATH = join(LLVM_BUILD_ROOT, "build/bin/opt")
CROSS_SYSROOT = join(TOOLCHAIN_ROOT, "mips-linux-gnu/libc")


INPUT_EXTENSION = ".c"
HEADER_EXTENSION = ".h"

EXCLUDE_LIST = [
    "polybench.c",
    "exptree.c",
    "flops.c",
    "perlin.c",
    # "linpack-pc.c",
    "flops.c",
    "perlin.c",
]

class Scope:
    def __init__(self):
        self.compilers = ['clang']
        self.entity = None
        self.opts = ['-O0', '-O1', '-O2', '-O3']
        self.domain = 'everything'
