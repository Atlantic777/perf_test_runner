"""
Just raw config data
"""

from os.path import (
    join,
    expanduser,
)

HOME = expanduser("~")
LLVM_BUILD_ROOT = join(HOME, "diplomski/build/llvm")

SINGLE_SOURCE_TESTS_ROOT = join(LLVM_BUILD_ROOT, "projects/test-suite/SingleSource/Benchmarks/")

OUTPUT_ROOT = join(HOME, "diplomski/test_runs/")

GCC_PATH = "/usr/bin/gcc"
CLANG_PATH = join(LLVM_BUILD_ROOT, "build/bin/clang")
OPT_PATH = join(LLVM_BUILD_ROOT, "build/bin/opt")

INPUT_EXTENSION = ".c"
HEADER_EXTENSION = ".h"

EXCLUDE_LIST = [
    "polybench.c",
    "exptree.c",
    # "linpack-pc.c",
]
