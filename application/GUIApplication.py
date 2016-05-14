from . import Application

from jobs import (
    CompilerOptions,
    FileExplorer,
    JobBuilder,
)

from widgets import (
    EntityManagerView,
    EntityView,
    InstanceView,
)

from PyQt4.QtGui import *
from PyQt4.QtCore import *

from models import EntityManagerListModel
from entity import *
from actions import *

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

        self.actions['find_sources'].on_triggered()

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
        self.instance_view = InstanceView()

        self.main.addWidget(self.job_list_view)
        self.job_list_view.width()

        self.main.addWidget(self.entity_widget)
        self.entity_widget.addWidget(self.entity_view)
        self.entity_widget.addWidget(self.instance_view)

        self.main.addWidget(self.actions_pane)

        self.layout.addWidget(self.main)

        self.main.setSizes([250, 800, 250])
        self.entity_widget.setSizes([100, 600])

        self.connect_signals()

    def connect_signals(self):
        entity_changed = self.job_list_view.entitySelectionChanged
        instance_changed = self.entity_view.instanceSelectionChanged

        entity_changed.connect(self.entity_view.entitySelectionChanged)
        entity_changed.connect(self.set_entity)

        instance_changed.connect(self.set_instance)
        instance_changed.connect(self.instance_view.setInstance)

    def fill_sources(self, sources):
        self.entity_manager.createEntityList(sources)
        self.job_list_view.model().endResetModel()

    def set_includes(self, includes):
        self.includes = includes

    def register_actions(self):
        self.actions = {}

        self._register_single_action('find_sources', FindSourcesAction)
        self._register_single_action('compile_instance', CompileInstanceAction)
        self._register_single_action('generate_ll', GenerateBitcodeAction)
        self._register_single_action('optim_stats', OptimiserStatsAction)

    def _register_single_action(self, name, action_class):
        self.actions[name] = action_class(self)
        self.actions_pane.registerAction(self.actions[name])

    @pyqtSlot(Entity)
    def set_entity(self, entity):
        self.selected_entity = entity
        self.selected_instance = None

    @pyqtSlot(EntityInstance)
    def set_instance(self, instance):
        self.selected_instance = instance