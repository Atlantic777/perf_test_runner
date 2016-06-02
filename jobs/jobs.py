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
    CROSS_GCC_PATH,
    CROSS_SYSROOT,
)

import subprocess
from utils import hashlib

from results import *

class JobBase:
    tag = None
    output_extension = None
    ResultClass = None

    def __init__(self, instance, includes=[]):
        if self.ResultClass is None:
            raise Exception("The JobClass is too abstract!")

        self.instance = instance
        self.includes = includes

        self.result = self.ResultClass(instance)

    def run(self, force=False, verbose=True):
        if force is False and self.ResultClass.tag in self.instance.results:
            return
        else:
            pass

        try:
            pipe = subprocess.PIPE
            args = self.get_args_list()
            proc = subprocess.Popen(args, stdout=pipe, stderr=pipe)

            (out, err) = proc.communicate()
            (out, err) = ( self._b2s(out), self._b2s(err) )

            if verbose:
                print(out)
                print(err)

            print("pre save results")
            self.collect_results(out, err)
        except Exception as e:
            print("exception happened")
            print(e)

    def get_args_list(self):
        raise Exception("not implemented!")

    def collect_results(self, out=None, err=None):
        pass

    def _b2s(self, b):
        return ''.join([chr(i) for i in b])

    # def get_output_path(self):
    #     if self.output_extension is None:
    #         raise Exception("output extension is not set!")

    #     d = self.instance.getOutputPath()
    #     f = self.instance.parent.source.name.replace('.c', self.output_extension)

        return path.join(d, f)

class CompilerJob(JobBase):
    ResultClass = CompilationResult

    def collect_results(self, out=None, err=None):
        out = self.result.action_output_file.full_path
        _hash = hash_of_file(out)
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

class CrossAsmJob(JobBase):
    ResultClass = CrossAsmResult

    def collect_results(self, out=None, err=None):
        print("saving results")
        self.result.save()

    def get_args_list(self):
        args = []
        args.append(self.instance.compiler.path)
        args.append("--sysroot")
        args.append(CROSS_SYSROOT)
        args.append("-S")
        args.append("--target=mips")
        args += ['-I' + include_folder for include_folder in self.includes]
        args.append(self.instance.opt)
        args.append(self.instance.parent.source.path)
        args.append("-o" + self.result.action_output_file.full_path)

        return args

class CrossCompileJob(JobBase):
    ResultClass = CrossCompileResult

    def collect_results(self, out=None, err=None):
        out = self.result.action_output_file.full_path
        self.result.save()

    def get_args_list(self):
        args = []
        args.append(CROSS_GCC_PATH)
        args.append("-lm")
        args.append("-EL")
        args += ['-I' + include_folder for include_folder in self.includes]
        args.append(self.instance.opt)
        args.append(self.instance.results[CrossAsmResult.tag].action_output_file.full_path)
        args.append("-o" + self.result.action_output_file.full_path)

        return args


class GenerateBitcodeJob(JobBase):
    ResultClass = GenerateBitcodeResult

    def get_args_list(self):
        args = [
            self.instance.compiler.path,
            "-emit-llvm",
            "-S",
            "--target=mips",
            self.instance.opt,
            self.instance.parent.source.path,
            "-o" + self.result.action_output_file.full_path,
        ]
        args += ['-I' + include_folder for include_folder in self.includes]

        return args

    def collect_results(self, out=None, err=None):
        self.result.save()

class GenerateOptimiserStatsJob(JobBase):
    ResultClass = OptimiserStatsResult

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
    ResultClass = PerfResult

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
    ResultClass = ExecutableSizeResult

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
    ResultClass = TimeExecutionResult

    def collect_results(self, out, err):
        self.result.raw_output = '\n'.join(err.split('\n')[-3:])
        self.result.save()

    def get_args_list(self):
        args = [
            'time',
            self.instance.results[CompilationResult.tag].action_output_file.full_path,
        ]

        return args

class TimeCrossJob(JobBase):
    ResultClass = TimeCrossResult

    def collect_results(self, out, err):
        self.result.raw_output = '\n'.join(err.split('\n')[-3:])
        self.result.save()

    def get_args_list(self):
        args = [
            'time',
            self.instance.results[CrossCompileResult.tag].action_output_file.full_path,
        ]

        return args

class PerfEstJob(JobBase):
    ResultClass = PerfEstResult

    def collect_results(self, out, err):
        self.result.raw_output = err
        self.result.save()

    def get_args_list(self):
        args = [
            OPT_PATH,
            "-analyze",
            "-perf-est",
            self.instance.results[GenerateBitcodeResult.tag].action_output_file.full_path
        ]

        return args

class PerfEstBackJob(JobBase):
    ResultClass = PerfEstBackResult

    def collect_results(self, out, err):
        self.result.raw_output = err
        self.result.save()

    def get_args_list(self):
        args = [
            CLANG_PATH,
            "--target=mips",
            "-S",
            self.instance.opt,
            self.instance.parent.source.path,
            "-o/dev/null"
        ]
        args += ['-I' + include_folder for include_folder in self.includes]

        return args
