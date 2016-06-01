"""
If an action produces output file,
then that file is stored here.

If an action analyses one file,
then result of that analysis can be stored
as string in file.

Every result object can be retrieved from entity's
results dict by it's tag.

Result can be saved or loaded to disk.

Result can be further parsed by a ResultParser,
and stored in result model.
"""
from files import File
from os import path
from utils import hash_of_file

from PyQt4.QtGui import (
    QTextBrowser,
    QFont,
)

from result_parsers import *

class Result:
    extension = None
    tag = None
    analysis_output_file = None
    action_output_file = None
    raw_output = None
    has_output = False
    has_analysis = False
    ParserClass = None
    parsed_data = None

    def __init__(self, instance):
        self.instance = instance
        self.name = self.instance.parent.source.name

        if self.extension and self.has_output:
            self.action_output_file = self.get_action_output_file()

        if self.has_analysis:
            self.analysis_output_file = self.get_analysis_output_file()

    def replaceExtension(self, extension):
        return self.name.replace('.c', extension)

    def get_action_output_file(self):
       p = self.instance.getOutputPath()
       act_name = self.replaceExtension(self.extension)

       return File(p, act_name)

    def get_analysis_output_file(self):
        p = self.instance.getOutputPath()
        analysis_name = self.replaceExtension(".res_" + self.tag)

        return File(p, analysis_name)

    def save(self):
        self.instance.results[self.tag] = self

        if self.raw_output is not None:
            with open(self.analysis_output_file.full_path, "w") as f:
                f.write(self.raw_output)

    def load(self):
        action_out = self.has_output and path.isfile(self.action_output_file.full_path)
        analysis_out = self.has_analysis and path.isfile(self.analysis_output_file.full_path)

        if analysis_out:
            with open(self.analysis_output_file.full_path) as f:
                self.raw_output = f.read()

        if action_out or analysis_out:
            self.instance.results[self.tag] = self
            return True
        else:
            return False

    def generate_report(self):
        report = ""

        if self.has_output:
            report += self.action_output_file.full_path + '\n'
            report += "-"*10 + '\n'

        if self.has_analysis:
            report += self.raw_output + '\n'
            report += "-"*10 + '\n'

        return report

    def parse(self):
        if self.ParserClass is None:
            raise Exception("parser is not implemented")
        else:
            parser = self.ParserClass(self.raw_output)
            self.parsed_data = parser.values

class CompilationResult(Result):
    extension = ".out"
    tag = "compilation"
    has_output = True

    def load(self):
        good = super().load()

        if good is True:
            self.instance._hash = hash_of_file(self.action_output_file.full_path)

class CrossCompileResult(Result):
    extension = ".xout"
    tag = "cross_comp"
    has_output = True

    def load(self):
        good = super().load()

class GenerateBitcodeResult(Result):
    extension = ".ll"
    tag = "bitcode"
    has_output = True

class OptimiserStatsResult(Result):
    tag = "optimiser_stats"
    has_analysis = True

class PerfResult(Result):
    tag = "perf"
    has_analysis = True
    ParserClass = PerfResultParser

class ExecutableSizeResult(Result):
    tag = "executable_size"
    has_analysis = True
    ParserClass = ExecutableSizeParser

class TimeExecutionResult(Result):
    tag = "execution_time"
    has_analysis = True
    ParserClass = TimeExecutionParser

class CrossAsmResult(Result):
    tag = "cross_asm"
    has_analysis = False
    has_output = True
    extension = "-x.s"

class TimeCrossResult(Result):
    tag = "cross_time"
    has_analysis = True

