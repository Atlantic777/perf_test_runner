"""
Application CLI - wrap everything together
"""
from jobs import (
    CompilerOptions,
    FileExplorer,
    JobBuilder,
)

from settings import (
    SINGLE_SOURCE_TESTS_ROOT,
)

from tasks import (
    CompilationTask,
    StaticAnalysisTask,
    DynamicAnalysisTask,
)

from widgets import (
    EntityManagerView,
    EntityView,
    InstanceView,
)

from models import EntityManagerListModel
from entity import *
from actions import *

from PyQt4.QtGui import *
from PyQt4.QtCore import *

class Application:
    def __init__(self):
        self.options = CompilerOptions()

        self._explorer = FileExplorer(SINGLE_SOURCE_TESTS_ROOT)
        (self.source_list, self.options.include_dirs) = self._explorer.find()

        self._job_builder = JobBuilder(self.options, self.source_list)
        self.jobs = self._job_builder.build_jobs()
        self._job_builder.make_output_dirs()


        self.tasks = [
            CompilationTask(workers=4, jobs=self.jobs),
            # StaticAnalysisTask(workers=4, jobs=self.jobs),
            # DynamicAnalysisTask(workers=1, jobs=self.jobs),
        ]

        self.actions = [
            CompilationTask,
        ]


    def run(self):
        for task in self.tasks:
            task.run()
