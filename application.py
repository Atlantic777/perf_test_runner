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

class ActionsPane(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.layout.addStretch()

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

        self.w.resize(1300, 700)
        self.w.setWindowTitle("# Hello world!")

        self.setup_entity_manager()
        self.build_layout()
        self.register_actions()

        self.selected_instance = None
        self.selected_entity = None

        self.w.show()

    def setup_entity_manager(self):
        self.build_options = CompilerOptions()
        self.entity_manager = EntityManager(self.build_options)

    def run(self):
        self.qApp.exec_()

    def build_layout(self):
        self.layout = QVBoxLayout()
        self.w.setLayout(self.layout)

        self.main = QSplitter()
        self.actions_pane = ActionsPane()

        self.entity_widget = QSplitter(Qt.Vertical)

        self.job_list_view = EntityManagerView(self.entity_manager)
        self.entity_view = EntityView()

        self.main.addWidget(self.job_list_view)
        self.job_list_view.width()

        self.main.addWidget(self.entity_widget)
        self.entity_widget.addWidget(self.entity_view)
        self.entity_widget.addWidget(QTextBrowser())

        self.job_list_view.entitySelectionChanged.connect(self.entity_view.entitySelectionChanged)
        self.job_list_view.entitySelectionChanged.connect(self.set_entity)

        self.entity_view.instanceSelectionChanged.connect(self.set_instance)

        self.main.addWidget(self.actions_pane)

        self.layout.addWidget(self.main)

        self.main.setSizes([250, 800, 250])

    def fill_sources(self, sources):
        self.entity_manager.createEntityList(sources)
        self.job_list_view.model().endResetModel()

    def set_includes(self, includes):
        self.includes = includes

    def register_actions(self):
        self.actions_pane.registerAction(FindSourcesAction(self))
        self.actions_pane.registerAction(CompileInstanceAction(self))

    @pyqtSlot(Entity)
    def set_entity(self, entity):
        self.entity = entity
        self.instance = None

    @pyqtSlot(EntityInstance)
    def set_instance(self, instance):
        self.instance = instance
