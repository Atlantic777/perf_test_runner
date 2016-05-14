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
