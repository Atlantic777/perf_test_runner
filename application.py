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

from widgets import EntityManagerView
from models import EntityManagerListModel
from entity import *

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


class JobListModel(QAbstractListModel):
    pass

class FindSourcesAction(QAction):
    title = "Find sources"

    def __init__(self, parent):
        super().__init__(self.title, parent, triggered=self.on_triggered)
        self.setParent(parent)

    def on_triggered(self, event):
        explorer = FileExplorer(SINGLE_SOURCE_TESTS_ROOT)
        (source_list, include_dirs) = explorer.find()

        self.parent().fill_sources(source_list)
        self.parent().set_includes(include_dirs)

class ActionsPane(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

    def registerAction(self, action):
        button = QToolButton()
        button.setDefaultAction(action)
        self.layout.addWidget(button)

class GUIApplication(Application, QObject):
    def __init__(self):
        super(Application, self).__init__()
        super(QObject, self).__init__()

        self.qApp = QApplication([])
        self.w = QWidget()

        self.w.resize(640, 480)
        self.w.setWindowTitle("# Hello world!")

        self.setup_entity_manager()
        self.build_layout()
        self.register_actions()

        self.w.show()

    def setup_entity_manager(self):
        self.build_options = CompilerOptions()
        self.entity_manager = EntityManager(self.build_options)

        (sources_list, include_list) = FileExplorer().find()

        self.entity_manager.createEntityList(sources_list)

    def run(self):
        self.qApp.exec_()

    def build_layout(self):
        self.layout = QVBoxLayout()
        self.w.setLayout(self.layout)

        self.main = QSplitter()
        self.actions_pane = ActionsPane()

        self.job_list_view = EntityManagerView(self.entity_manager)

        self.main.addWidget(self.job_list_view)
        self.main.addWidget(QTextBrowser())
        self.main.addWidget(self.actions_pane)

        self.layout.addWidget(self.main)

    def fill_sources(self, sources):
        print("Filling sources")

    def set_includes(self, includes):
        pass

    def register_actions(self):
        self.actions_pane.registerAction(FindSourcesAction(self))
