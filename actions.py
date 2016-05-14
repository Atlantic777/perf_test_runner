from PyQt4.QtGui import QAction
from settings import *

from jobs import (
    FileExplorer,
    CompilerJob,
    GenerateBitcodeJob,
)

class MetaAction(QAction):
    def __init__(self, parent=None):
        super().__init__(self.title, parent, triggered=self.on_triggered)
        self.setParent(parent)

    def on_triggered(self, event):
        print("Action not implemented!")

class FindSourcesAction(MetaAction):
    title = "Find sources"

    def on_triggered(self, event=None):
        explorer = FileExplorer(SINGLE_SOURCE_TESTS_ROOT)
        (source_list, include_dirs) = explorer.find()

        self.parent().fill_sources(source_list)
        self.parent().set_includes(include_dirs)

class CompileInstanceAction(MetaAction):
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

class GenerateBitcode(MetaAction):
    title = "Generate LLVM IR"

    def on_triggered(self, event):
        instance = self.parent().selected_instance

        if instance is None or instance.compiler.name != 'clang':
            print("can't do that")
        else:
            job = GenerateBitcodeJob(instance)
            job.run()
            self.parent().instance_view.refresh()