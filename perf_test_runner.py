#!/usr/bin/python3
from multiprocessing import Pool
from time import sleep

from os import (
    walk,
    path,
    makedirs,
    chdir,
    )

SINGLE_SOURCE_TESTS_ROOT = "/home/rtrk/code/llvm/projects/test-suite/SingleSource/Benchmarks/"
OUTPUT_ROOT = "/home/rtrk/code/diplomski/test_runs/"

class File:
    name = None
    path = None

    def __init__(self, name, path):
        self.name = name
        self.path = path

    def __str__(self):
        return "File: " + self.name + " " + self.path

class Compiler(File):
    pass

class SourceFile(File):
    pass

class CompilerOptions:
    compilers_list = None
    optim_levels_list = None

    def __init__(self):
        self.compilers_list = [
            Compiler("gcc", "/usr/bin/gcc"),
            Compiler("clang", "/home/rtrk/code/diplomski/llvm/build/bin//clang"),
        ]

        self.optim_levels_list = [
            "-O0",
            "-O1",
            "-O2",
            "-O3",
            "-Os",
        ]

    def __str__(self):
        s = ""
        s += "##### BEGIN COMPILER OPTIONS SETUP ######\n"
        s += "Compilers:" 
        s += "\n---------------\n"

        for c in self.compilers_list:
            s += str(c) + '\n'

        s += "\nOptimization levels:"
        s += "\n---------------\n"
        s +=", ".join(self.optim_levels_list)

        s += "\n#### END COMPILER OPTIONS SETUP #####"

        return s

class Job:
    compiler = None
    optim_level = None
    source = None
    output = None
    static_prediction = None
    static_log = None
    dynamic_time = None

class FileExplorer:
    root = None
    self.input_extension = ".c"
    self.EXCLUDE_LIST = [
        "polybench.c",
        ".exptree.c",
    ]

    def __init__(self, root):
        self.root = root

    def find(self):
        for root, dirs, files in walk(self.root):
            for f in files:
                if f.endswith(self.INPUT_EXTENSION) and f not in self.EXCLUDE_LIST:
                    abs_path = path.join(root, f)
                    INPUT_FILES.append( (abs_path, f) )
                elif f.endswith(HEADER_FILE_EXTENSION):
                    INCLUDE_DIRS.append(root)
        return []

class JobBuilder:
    compiler_options = None
    source_list = None
    jobs = None

    def build_jobs(self):
        return []

class CompilationTask:
    pass

class StaticAnalysisTask:
    pass

class DynamicAnalysisTask:
    pass

class Application:
    def __init__(self):
        self.options = CompilerOptions()

        self._explorer = FileExplorer(SINGLE_SOURCE_TESTS_ROOT)
        self.source_list = self._explorer.find()

        self._job_builder = JobBuilder(options, self.source_list)
        self.jobs = job_builder.build_jobs()

    def run(self):
        print("running app!")


def compile(arg):
    print(arg)
    sleep(5)

if __name__ == "__main__":
    a = Application()
    a.run()
