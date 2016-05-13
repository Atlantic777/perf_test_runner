from files import (
    Compiler,
    SourceFile,
)

from os import (
    walk,
    path,
    makedirs,
    chdir,
    )

from settings import (
    GCC_PATH,
    CLANG_PATH,
    INPUT_EXTENSION,
    HEADER_EXTENSION,
    EXCLUDE_LIST,
    OUTPUT_ROOT,
    SINGLE_SOURCE_TESTS_ROOT,
)

import subprocess
import hashlib

class CompilerOptions:
    compilers_list = None
    optim_levels_list = None
    include_dirs = None

    def __init__(self):
        self.compilers_list = [
            Compiler(name="gcc", path=GCC_PATH),
            Compiler(name="clang", path=CLANG_PATH),
        ]

        self.optim_levels_list = [
            "-O0",
            "-O1",
            "-O2",
            "-O3",
            "-Os",
        ]

    def get_output_dirs(self):
        d = []

        for compiler in self.compilers_list:
            for opt in self.optim_levels_list:
                d.append(path.join(compiler.name, opt.strip('-').lower()))

        return d

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

    def get_include_dirs(self):
        includes = ""

        for i in self.include_dirs:
            includes += "-I" + i + ' '

        return includes


class Job:
    compiler = None
    optim_level = None
    source = None
    output = None
    static_prediction = None
    static_log = None
    dynamic_time = None
    includes = None
    libs = None

    def set_output(self, root):
        d = path.join(root, str(self.compiler), self.optim_level.strip('-').lower())
        f = str(self.source).replace('.c', '.out')

        self.output = path.join(d, f)

    def set_includes(self, includes):
        self.includes = includes

    def __str__(self):
        return "Job: " + self.get_cmd()

    def get_cmd(self):
        cmd = self.compiler.path + ' ' + self.get_cmd_args()
        return cmd

    def get_cmd_args(self):
        args = ""
        args += "-lm "
        args += self.includes
        args +=  self.optim_level + ' ' + self.source.path
        args += " -o" + self.output
        return args

    def __repr__(self):
        return self.compiler + " " + self.source

class FileExplorer:
    root = None

    input_files = []
    include_dirs = []


    def __init__(self, root=SINGLE_SOURCE_TESTS_ROOT):
        self.root = root

    def find(self):
        for root, dirs, files in walk(self.root):
            for f in files:
                if f.endswith(INPUT_EXTENSION) and f not in EXCLUDE_LIST:
                    abs_path = path.join(root, f)
                    self.input_files.append( SourceFile(abs_path, f) )
                elif f.endswith(HEADER_EXTENSION):
                    self.include_dirs.append(root)
        return (self.input_files, self.include_dirs)

class JobBuilder:
    compiler_options = None
    source_list = None
    jobs = None

    def __init__(self, options, source_list):
        self.source_list = source_list
        self.compiler_options = options
        self.jobs = []

    def build_jobs(self):
        for src in self.source_list:
            self.jobs += self._jobs_for_source(src)

        return self.jobs

    def _jobs_for_source(self, src):
        jobs = []

        for compiler in self.compiler_options.compilers_list:
            for opt in self.compiler_options.optim_levels_list:
                job = Job()
                job.compiler = compiler
                job.optim_level = opt
                job.source = src
                job.set_output(OUTPUT_ROOT)
                jobs.append(job)
                job.set_includes(self.compiler_options.get_include_dirs())

        return jobs

    def make_output_dirs(self):
        try:
            for d in self.compiler_options.get_output_dirs():
                makedirs(path.join(OUTPUT_ROOT, d))
        except:
            pass

class CompilerJob:
    includes = None
    instance = None

    def __init__(self, instance, includes):
        self.includes = includes

        self.instance = instance
        self.instance.results['compilation_output_path'] = self.get_output_path()

    def get_output_path(self):
        compiler = self.instance.compiler.name
        optim = self.instance.opt

        d = path.join(OUTPUT_ROOT, compiler, optim.strip('-').lower())
        f = self.instance.parent.source.name.replace('.c', '.out')

        return path.join(d, f)

    def run(self):
        try:
            resp = subprocess.call(self.get_cmd_args_list(), stderr=subprocess.STDOUT)

            out = self.instance.results['compilation_output_path']
            _hash = hashlib.md5(open(out, "rb").read()).hexdigest()
            self.instance._hash = _hash

        except subprocess.CalledProcessError as e:
            print(e.output)
            self.instance.results.pop('compilation_output_path')

        except Exception as e:
            print(e)

    def get_cmd_args_list(self):
        args = []
        args.append(self.instance.compiler.path)
        args.append("-lm")
        args += ['-I' + include_folder for include_folder in self.includes]
        args.append(self.instance.opt)
        args.append(self.instance.parent.source.path)
        args.append("-o" + self.get_output_path())

        return args
