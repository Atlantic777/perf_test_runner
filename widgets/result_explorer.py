from PyQt4.QtGui import (
    QWidget,
    QSplitter,
    QItemSelectionModel,
)

from PyQt4.QtCore import (
    Qt
)

from . import *
from actions import *


class EntityWidget(QSplitter):
    def __init__(self):
        super().__init__(Qt.Vertical)

        self.entity_view = EntityView()
        self.instance_view = InstanceView()

        self.addWidget(self.entity_view)
        self.addWidget(self.instance_view)

class ResultExplorer(QSplitter):
    def __init__(self, entity_manager):
        super().__init__()
        self.entity_manager = entity_manager

        self.build_layout()
        self.register_actions()
        self.connect_signals()

        self.setSizes([250, 800, 250])
        self.entity_widget.setSizes([100, 600])

        self.selected_entity = None
        self.selected_instance = None

        self.instance_type = None

        self.includes = self.entity_manager.include_dirs


    def build_layout(self):
        # get job_list_view
        self.job_list_view = EntityManagerView(self.entity_manager)
        self.addWidget(self.job_list_view)

        # get entity_widget
        self.entity_widget = EntityWidget()
        self.entity_view = self.entity_widget.entity_view
        self.instance_view = self.entity_widget.instance_view
        self.addWidget(self.entity_widget)

        # get action_pane
        self.actions_pane = ActionsPane()
        self.addWidget(self.actions_pane)

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
        self._register_single_action('perf', PerfAction)
        self._register_single_action('size', SizeAction)
        self._register_single_action('time', TimeAction)
        self._register_single_action('perf est', PerfEstAction)

    def _register_single_action(self, name, action_class):
        self.actions[name] = action_class(self)
        self.actions_pane.registerAction(self.actions[name])

    @pyqtSlot(Entity)
    def set_entity(self, entity):
        self.selected_entity = entity
        self.selected_instance = None

        if self.instance_type is not None:
            self.entity_view.selectInstanceType(self.instance_type)

    @pyqtSlot(EntityInstance)
    def set_instance(self, instance):
        self.selected_instance = instance
        self.instance_type = (instance.compiler.name, instance.opt)

    def getActionScopes(self):
        scopes = self.actions_pane.scope_widget.get_scopes()
        return scopes

        # return self.actions_pane.scope_widget.group.checkedId()


