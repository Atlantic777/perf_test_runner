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

class Result:
    extension = None
    tag = None
    analysis_output_file = None
    action_output_file = None
    raw_output = None
    has_output = False
    has_analysis = False

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

class CompilationResult(Result):
    extension = ".out"
    tag = "compilation"
    has_output = True

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

class ExecutableSizeResult(Result):
    tag = "executable_size"
    has_analysis = True

class TimeExecutionResult(Result):
    tag = "execution_time"
    has_analysis = True
