"""
Wraps job into QAction objects

Such objects can easibly be assigned to QButtons
and added to an ActionBar

Don't implement business logic here. Use jobs module for that.
"""
from PyQt4.QtGui import QAction
from settings import *

from jobs import *
from results import  *

class MetaAction(QAction):
    """
    Abstract class for actions

    Just define on_triggered function
    You can expect root window to be available in self.parent

    This is actually an action executor. It will fetch scope,
    filter out instances and then run the self.run() function
    on each instance.

    After that it will refresh all widgets.
    """

    def __init__(self, parent=None):
        super().__init__(self.title, parent, triggered=self.on_triggered)
        self.setParent(parent)
        self.set_dependencies()

    def on_triggered(self, event=None):
        self.scopes = self.parent().getActionScopes()
        self.instance_list = self.getInstances(self.scopes)

        self.triggerIt()

    def triggerIt(self):
        for instance in self.instance_list:
            if self.check_dependencies(instance) is True:
                self.run(instance)
            else:
                print("Can't do that!")

        self.refresh_widgets()


    def getInstances(self, scopes):
        entities = self._getEntities(scopes)
        instances = self._filterInstances(entities, scopes)

        return instances

    def _getEntities(self, scopes):
        s = scopes['entity']

        parent = self.parent()
        entity_manager = parent.entity_manager

        entities = None

        if s == 0:
            entities = entity_manager.all_instances()
        elif (s == 1 or s == 2) and parent.selected_entity is not None:
            entities = parent.selected_entity.all_instances()
        else:
            entities = []

        return entities

    def _filterInstances(self, instances, scopes):
        final_instances_list = []

        parent = self.parent()
        selected_entity = parent.selected_entity
        selected_instance = parent.selected_instance

        if scopes['entity'] == 2 and selected_instance is not None:
            return  [ selected_instance ]

        for instance in instances:
            if self._checkSingleInstance(instance, scopes):
                final_instances_list.append(instance)

        return final_instances_list

    def _checkSingleInstance(self, instance, scopes):
        selected_compilers = scopes['compiler']
        selected_optims = scopes['optimisation']

        compiler_ok = instance.compiler.name in selected_compilers
        optim_ok = instance.opt in selected_optims

        if compiler_ok and optim_ok:
            return True
        else:
            return False

    def check_dependencies(self, instance):
        if self.dependencies is None:
            return True
        else:
            are_ok = True

            for dependency in self.dependencies:
                are_ok = are_ok and dependency(instance)

            return are_ok

    def run(self, instance):
        if self.JobClass is not None:
            print(instance)
            self.job = self.JobClass(instance)
            self.job.run()

    def is_clang(self, instance):
        return (instance.compiler.name == "clang")

    def has_bitcode(self, instance):
        return GenerateBitcodeResult.tag in instance.results

    def has_executable(self, instance):
        return CompilationResult.tag in instance.results

    def refresh_widgets(self):
        self.parent().entity_view.refresh()
        self.parent().instance_view.refresh()
        self.parent().job_list_view.refresh()

    def set_dependencies(self):
        self.dependencies = None

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

    def run(self, instance):
        includes = self.parent().includes
        job = CompilerJob(instance, includes)
        job.run()


class GenerateBitcodeAction(MetaAction):
    """
    Create GenerateBitcodeJob and run it
    """
    title = "Generate LLVM IR"

    def set_dependencies(self):
        self.dependencies = [
            self.is_clang,
        ]

    def run(self, instance):
        includes = self.parent().includes
        job = GenerateBitcodeJob(instance, includes)
        job.run()


class OptimiserStatsAction(MetaAction):
    """
    Create GenerateOptimiserStatsJob

    Works only for LLVM -O{1,2,3,s} instances
    """
    title = "Get optimiser stats"
    JobClass = GenerateOptimiserStatsJob

    def set_dependencies(self):
        self.dependencies = [
            self.has_bitcode,
            self.is_clang,
            self.check_optim_level,
        ]

    def check_optim_level(self, instance):
        return not instance.opt == '-O0'

class PerfAction(MetaAction):
    """
    Measure execution performance stats (IPC!) with perf tool.
    """
    title = "Perf measuring stats"
    JobClass = PerfJob

    def set_dependencies(self):
        self.dependencies = [
            self.has_executable,
        ]

class SizeAction(MetaAction):
    """
    Measure size of executable (ELF)
    """
    title = "Measure with size"
    JobClass = ExecutableSizeJob

    def set_dependencies(self):
        self.dependencies = [
            self.has_executable,
        ]

class TimeAction(MetaAction):
    """
    Measure execution time
    """
    title = "Measure execution time"
    JobClass = TimeExecutionJob

    def set_dependencies(self):
        self.dependencies = [
            self.has_executable,
        ]
