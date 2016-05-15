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

from results import *

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

        d = self.instance.getOutputPath()
        f = self.instance.parent.source.name.replace('.c', self.output_extension)

        return path.join(d, f)

class CompilerJob(JobBase):
    def __init__(self, instance, includes=None):
        super().__init__(instance)

        self.includes = includes
        self.result = CompilationResult(self.instance)

    def collect_results(self, out=None, err=None):
        out = self.result.action_output_file.full_path
        _hash = hashlib.md5(open(out, "rb").read()).hexdigest()
        self.instance._hash = _hash

        self.result.save()

    def get_args_list(self):
        args = []
        args.append(self.instance.compiler.path)
        args.append("-lm")
        args += ['-I' + include_folder for include_folder in self.includes]
        args.append(self.instance.opt)
        args.append(self.instance.parent.source.path)
        args.append("-o" + self.result.action_output_file.full_path)

        return args

class GenerateBitcodeJob(JobBase):
    def __init__(self, instance, includes):
        super().__init__(instance)
        self.includes = includes

        self.result = GenerateBitcodeResult(self.instance)

    def get_args_list(self):
        args = [
            self.instance.compiler.path,
            "-emit-llvm",
            "-S",
            "-O0",
            self.instance.parent.source.path,
            "-o" + self.result.action_output_file.full_path,
        ]
        args += ['-I' + include_folder for include_folder in self.includes]

        return args

    def collect_results(self, out=None, err=None):
        self.result.save()

class GenerateOptimiserStatsJob(JobBase):
    def __init__(self, instance):
        super().__init__(instance)
        self.result = OptimiserStatsResult(self.instance)

    def collect_results(self, out, err):
        self.result.raw_output = err
        self.result.save()

    def get_args_list(self):
        args = [
            OPT_PATH,
            "-stats",
            self.instance.opt,
            self.instance.results[GenerateBitcodeResult.tag].action_output_file.full_path,
            "-o",
            "/dev/null",
        ]

        return args

class PerfJob(JobBase):
    def __init__(self, instance):
        super().__init__(instance)
        self.result = PerfResult(instance)

    def collect_results(self, out, err):
        self.result.raw_output = err
        self.result.save()

    def get_args_list(self):
        args = [
            "perf",
            "stat",
            self.instance.results[CompilationResult.tag].action_output_file.full_path
        ]

        return args

class ExecutableSizeJob(JobBase):
    def __init__(self, instance):
        super().__init__(instance)
        self.result = ExecutableSizeResult(instance)

    def collect_results(self, out, err):
        self.result.raw_output = out
        self.result.save()

    def get_args_list(self):
        args = [
            'size',
            self.instance.results[CompilationResult.tag].action_output_file.full_path,
        ]

        return args

class TimeExecutionJob(JobBase):
    def __init__(self, instance):
        super().__init__(instance)
        self.result = TimeExecutionResult(instance)

    def collect_results(self, out, err):
        self.result.raw_output = err
        self.result.save()

    def get_args_list(self):
        args = [
            'time',
            self.instance.results[CompilationResult.tag].action_output_file.full_path,
        ]

        return args
