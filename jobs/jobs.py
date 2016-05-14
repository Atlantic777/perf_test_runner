"""
new jobs module
"""

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
    OPT_PATH,
)

import subprocess
import hashlib

class JobBase:
    tag = None
    output_extension = None

    def __init__(self, instance):
        self.instance = instance

    def run(self):
        try:
            pipe = subprocess.PIPE
            args = self.get_args_list()
            proc = subprocess.Popen(args, stdout=pipe, stderr=pipe)

            (out, err) = proc.communicate()
            (out, err) = ( self._b2s(out), self._b2s(err) )

            self.collect_results(out, err)
        except Exception as e:
            print(e)

    def get_args_list(self):
        raise Exception("not implemented!")

    def collect_results(self, out=None, err=None):
        pass

    def _b2s(self, b):
        return ''.join([chr(i) for i in b])

    def get_output_path(self):
        if self.output_extension is None:
            raise Exception("output extension is not set!")

        compiler = self.instance.compiler.name
        optim = self.instance.opt

        d = path.join(OUTPUT_ROOT, compiler, optim.strip('-').lower())
        f = self.instance.parent.source.name.replace('.c', self.output_extension)

        return path.join(d, f)

class CompilerJob(JobBase):
    includes = None
    instance = None
    output_extension = ".out"

    def __init__(self, instance, includes):
        super().__init__(instance)

        self.includes = includes
        self.instance.results['compilation_output_path'] = self.get_output_path()

    def collect_results(self, out=None, err=None):
        out = self.instance.results['compilation_output_path']
        _hash = hashlib.md5(open(out, "rb").read()).hexdigest()
        self.instance._hash = _hash

    def get_args_list(self):
        args = []
        args.append(self.instance.compiler.path)
        args.append("-lm")
        args += ['-I' + include_folder for include_folder in self.includes]
        args.append(self.instance.opt)
        args.append(self.instance.parent.source.path)
        args.append("-o" + self.get_output_path())

        return args

class GenerateBitcodeJob:
    def __init__(self, instance, includes):
        self.instance = instance
        self.out = self.get_output_path()
        self.includes = includes

    def run(self):
        try:
            subprocess.check_call(self.get_cmd_args_list(), stderr=subprocess.STDOUT)
            self.instance.results['bitcode_path'] = self.out
        except subprocess.CalledProcessError as e:
            print(e)
        except Exception as e:
            print(e)

    def get_output_path(self):
        compiler = self.instance.compiler.name
        optim = self.instance.opt

        d = path.join(OUTPUT_ROOT, compiler, optim.strip('-').lower())
        f = self.instance.parent.source.name.replace('.c', '.ll')

        return path.join(d, f)

    def get_cmd_args_list(self):
        args = [
            self.instance.compiler.path,
            "-emit-llvm",
            "-S",
            "-O0",
            self.instance.parent.source.path,
            "-o" + self.out,
        ]
        args += ['-I' + include_folder for include_folder in self.includes]

        return args

class GenerateOptimiserStatsJob:
    def __init__(self, instance):
        self.instance = instance

    def run(self):
        p = subprocess.Popen(self.get_args_list(),  stderr=subprocess.PIPE)
        out, err = p.communicate()

        self.instance.results['opt_stats'] = ''.join([chr(i) for i in err])

    def get_args_list(self):
        args = [
            OPT_PATH,
            "-stats",
            self.instance.opt,
            self.instance.results['bitcode_path'],
            "-o",
            "/dev/null",
        ]

        return args


class PerfJob:
    def __init__(self, instance):
        self.instance = instance

    def run(self):
        p = subprocess.Popen(self.get_args_list(), stderr=subprocess.PIPE)
        out, err = p.communicate()

        self.instance.results['perf_stats'] = ''.join([chr(i) for i in err])

    def get_args_list(self):
        args = [
            "perf",
            "stat",
            self.instance.results['compilation_output_path']
        ]

        return args

class ExecutableSizeJob:
    def __init__(self, instance):
        self.instance = instance

    def run(self):
        p = subprocess.Popen(self.get_args_list(), stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        out, err = p.communicate()

        self.instance.results['executable_size'] = ''.join([chr(i) for i in out])

    def get_args_list(self):
        args = [
            'size',
            self.instance.results['compilation_output_path'],
        ]

        return args

class TimeExecutionJob:
    def __init__(self, instance):
        self.instance = instance

    def run(self):
        p = subprocess.Popen(self.get_args_list(), stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        out, err = p.communicate()

        self.instance.results['execution_time'] = ''.join([chr(i) for i in err])

    def get_args_list(self):
        args = [
            'time',
            self.instance.results['compilation_output_path'],
        ]

        return args
