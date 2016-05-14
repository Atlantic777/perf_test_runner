"""
Wraps job into QAction objects

Such objects can easibly be assigned to QButtons
and added to an ActionBar

Don't implement business logic here. Use jobs module for that.
"""
from PyQt4.QtGui import QAction
from settings import *

from jobs import *

class MetaAction(QAction):
    """
    Abstract class for actions

    Just define on_triggered function
    You can expect root window to be available in self.parent
    """
    def __init__(self, parent=None):
        super().__init__(self.title, parent, triggered=self.on_triggered)
        self.setParent(parent)

    def on_triggered(self, event):
        print("Action not implemented!")

class FindSourcesAction(MetaAction):
    """
    Start test source files discovery using FileExplorer
    """
    title = "Find sources"

    def on_triggered(self, event=None):
        explorer = FileExplorer(SINGLE_SOURCE_TESTS_ROOT)
        (source_list, include_dirs) = explorer.find()

        self.parent().fill_sources(source_list)
        self.parent().set_includes(include_dirs)

class CompileInstanceAction(MetaAction):
    """
    If instance is selected, create CompilerJob and run it.
    """
    title = "Compile instance"

    def on_triggered(self, event):
        instance = self.parent().selected_instance
        includes = self.parent().includes

        if instance is None:
            print("No instance selected!")
        else:
            print(instance)
            job = CompilerJob(instance, includes)
            job.run()
            self.parent().entity_view.refresh()

class GenerateBitcodeAction(MetaAction):
    """
    Create GenerateBitcodeJob and run it
    """
    title = "Generate LLVM IR"

    def on_triggered(self, event):
        instance = self.parent().selected_instance
        includes = self.parent().includes

        if instance is None or instance.compiler.name != 'clang':
            print("can't do that")
        else:
            job = GenerateBitcodeJob(instance, includes)
            job.run()
            self.parent().instance_view.refresh()

class OptimiserStatsAction(MetaAction):
    """
    Create GenerateOptimiserStatsJob

    Works only for LLVM -O{1,2,3,s} instances
    """
    title = "Get optimiser stats"

    def on_triggered(self, event):
        instance = self.parent().selected_instance

        if (
                instance is None
                or 'bitcode_path' not in instance.results
                or instance.compiler.name != 'clang'
                or instance.opt == '-O0'
        ):
            print("can't do that")
        else:
            job = GenerateOptimiserStatsJob(instance)
            job.run()
            self.parent().instance_view.refresh()


class PerfAction(MetaAction):
    """
    Measure execution performance stats (IPC!) with perf tool.
    """
    title = "Perf measuring stats"

    def on_triggered(self, event):
        instance = self.parent().selected_instance

        if (
                instance is None
                or 'compilation_output_path' not in instance.results
        ):
            print("can't do that")
        else:
            job = PerfJob(instance)
            job.run()
            self.parent().instance_view.refresh()

class SizeAction(MetaAction):
    """
    Measure size of executable (ELF)
    """
    title = "Measure with size"

    def on_triggered(self, event):
        instance = self.parent().selected_instance

        if (
                instance is None
                or 'compilation_output_path' not in instance.results
        ):
            print("can't do that")
        else:
            job = ExecutableSizeJob(instance)
            job.run()
            self.parent().instance_view.refresh()

