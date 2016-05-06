from os.path import join

HOME = "/home/nikola/"
LLVM_BUILD_ROOT = join(HOME, "diplomski/build/llvm")

SINGLE_SOURCE_TESTS_ROOT = join(LLVM_BUILD_ROOT, "projects/test-suite/SingleSource/Benchmarks/")

OUTPUT_ROOT = join(HOME, "diplomski/test_runs/")

GCC_PATH = "/usr/bin/gcc"
CLANG_PATH = join(LLVM_BUILD_ROOT, "build/bin/clang")

INPUT_EXTENSION = ".c"
HEADER_EXTENSION = ".h"

EXCLUDE_LIST = [
    "polybench.c",
    ".exptree.c",
]
