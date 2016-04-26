#!/usr/bin/python2
from os import (
    walk,
    path,
    makedirs,
    chdir,
    )

from os.path import basename

from subprocess import (
    check_call,
    call,
    Popen,
    PIPE,
    STDOUT,
    )

from glob import glob
from threading import (
    Thread,
    )

import sys
import signal

INPUT_FILES = []

SINGLE_SOURCE_TESTS_ROOT = "/home/rtrk/code/llvm/projects/test-suite/SingleSource/Benchmarks/"
OUTPUT_ROOT = "/home/rtrk/code/diplomski/test_runs/"
INPUT_FILE_EXTENSION = ".c"
HEADER_FILE_EXTENSION = ".h"
JOBS=6
BR = ' \\\n'

OPTIM_LEVELS = [
    'O0',
    'O1',
    'O2',
    'O3',
    'Os',
]

CLANG_PATH = "/home/rtrk/code/llvm/build/bin/clang"
GCC_PATH = "/usr/bin/gcc"
INCLUDE_DIRS = []

COMPILER_COMMANDS = {
    "gcc" : GCC_PATH,
    "clang" : CLANG_PATH,
}

def prepare_inputs():
    for root, dirs, files in walk(SINGLE_SOURCE_TESTS_ROOT):
        for f in files:
            if f.endswith(INPUT_FILE_EXTENSION) and f != "polybench.c" and f != "exptree.c":
                abs_path = path.join(root, f)
                INPUT_FILES.append( (abs_path, f) )
            elif f.endswith(HEADER_FILE_EXTENSION):
                INCLUDE_DIRS.append(root)

def prepare_output_locations():
    for compiler in COMPILER_COMMANDS:
        for level in OPTIM_LEVELS:
            p = path.join(OUTPUT_ROOT, compiler, level)

            try:
                makedirs(p)
            except:
                print("already existing?")

def static_analysis():
    for compiler in COMPILER_COMMANDS:
        for level in OPTIM_LEVELS:
            print("running static analysis")
            this_path = path.join(OUTPUT_ROOT, compiler, level)
            cmd = []
            cmd.append("md5sum")
            cmd += glob(path.join(this_path, "*.out"))

            f = open(path.join(this_path, "hashes.md5"), "w")
            p = Popen(cmd, stdout=f)
            p.wait()
            f.close()

def compiler_cmd(input_file_tuple, compiler, optim_level, thread_id=None, log_file=None):
    (input_abs_path, input_basename) = input_file_tuple
    output_name = input_basename.replace('.c', '.out')

    cmd = []
    cmd.append(COMPILER_COMMANDS[compiler])
    cmd.append(input_abs_path)
    cmd.append("-lm")


    for d in INCLUDE_DIRS:
        cmd.append("-I"+d)

    cmd.append('-' + optim_level)
    cmd.append("-o" + path.join(OUTPUT_ROOT, compiler, optim_level, output_name))


    if path.exists(output_name) is False:
        null = open("/dev/null", "w")
        p = Popen(cmd, stdout=null, stderr=STDOUT)
        # p = Popen(cmd)
        null.close()
        p.wait()
        # print(cmd)

def dynamic_analysis(input_file_tuple, compiler, level, thread_id=None, log_file=None):
        this_path = path.join(OUTPUT_ROOT, compiler, level)
        (input_abs_path, input_basename) = input_file_tuple

        prog_filename = input_basename.replace(".c", ".out")
        prog = path.join(this_path, prog_filename)

        cmd = ["time", '-f', '%C, %U, %E', "-o", log_file.name, "-a", prog]
        print cmd
        print ' '.join(cmd)
        p = Popen(cmd)
        p.wait()

def generate_output_with(procedure, input_files_batch=INPUT_FILES, thread_id=None, log_suffix=None):
    for compiler in COMPILER_COMMANDS.keys():
        for level in OPTIM_LEVELS:
            f = None
            if log_suffix is not None and thread_id is not None:
                f = open(path.join(OUTPUT_ROOT, compiler, level, log_suffix + "_" + str(thread_id) + ".log"), "w")

            for input_tuple in input_files_batch:
                procedure(input_tuple, compiler, level, thread_id, f)

            if f is not None:
                f.close()

def spawn_job(job_routine, log_suffix=None):
    print("start of spawn jobs")
    n = len(INPUT_FILES)/(JOBS)
    br = [(i,i+n) for i in range(0, len(INPUT_FILES)-n, n)]
    batches = []
    threads = []

    for b in br:
        batches.append(INPUT_FILES[b[0]:b[1]])

    batches[-1] += INPUT_FILES[br[-1][1]:]

    for i in range(JOBS):
        t = Thread(target=generate_output_with, args=(job_routine, batches[i], i, log_suffix))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    print("end of spawn jobs")

def collect_results():
    # set current compiler
    for compiler in COMPILER_COMMANDS.keys():
        # set current optim level
        for level in OPTIM_LEVELS:
            chdir(path.join(OUTPUT_ROOT, compiler, level))
            hashes = {}
            timings = {}

            # load hashes into a dict
            with open("hashes.md5") as f:
                for line in f.xreadlines():
                    (h, p) = line.split('  ')
                    b = basename(p).strip('.out\n')
                    hashes[b] = h

            # load timing into a dict
            for timing_output in glob("timing_output*"):
                with open(timing_output) as f:
                    for line in f.xreadlines():
                        line = line.replace('"', '').strip(' ').strip('\n')

                        try:
                            (a, b, c) = line.split(', ')
                            name = basename(a).strip('.out\n')
                            cpu_time = b
                            real_time = c

                            timings[name] = (b, c)

                        except:
                            print line

            # match data and write as csv
            with open("result_file.csv", "w") as f:
                for test in hashes.keys():
                    try:
                        h = hashes[test]
                        (cpu_time, real_time) = timings[test]
                        line = ','.join([test, compiler, level, h, cpu_time, real_time]) + '\n'
                        f.write(line)
                    except:
                        # print compiler, level, test
                        pass


def main():
    prepare_inputs()
    prepare_output_locations()

    spawn_job(compiler_cmd)
    static_analysis()
    spawn_job(dynamic_analysis, log_suffix="timing_output")

    # collect measure results
    collect_results()

if __name__ == "__main__":
    main()

