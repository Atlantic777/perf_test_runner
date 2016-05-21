"""
QWidgets for representing models of raw data
"""
from PyQt4.QtGui import (
    QListView,
    QWidget,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QTableView,
    QAbstractItemView,
    QTextBrowser,
    QFont,
    QToolButton,
    QGroupBox,
    QPushButton,
    QRadioButton,
    QButtonGroup,
    QCheckBox,
    QSizePolicy,
    QItemSelectionModel,
    QHeaderView,
    QTabWidget,
    QGridLayout,
)
from PyQt4.QtCore import (
    pyqtSlot,
    pyqtSignal,
)

from entity import (
    Entity,
    EntityInstance,
)

from models import (
    EntityManagerListModel,
    EntityTableModel,
)

from results import *
from .result_widgets import *

from jobs import CompilerOptions

class ScopeBox(QGroupBox):
    title = None
    button_type = None

    def __init__(self):
        if self.title is None or self.button_type is None:
            raise Exception("Still too abstract!")

        super().__init__(title=self.title)

        self.populate_button_id()
        self.build_layout()
        self.populate_box()
        self.select_default()

        if self.button_type == 'check':
            self.group.setExclusive(False)

    def populate_button_id(self):
        pass

    def build_layout(self):
        self.group = QButtonGroup()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

    def populate_box(self):
        keys = list(self.button_id.keys())
        keys.sort()

        BtnClass = None
        if self.button_type == 'check':
            BtnClass = QCheckBox
        elif self.button_type == 'radio':
            BtnClass = QRadioButton

        for key in keys:
            btn = BtnClass(key)
            self.layout.addWidget(btn)
            self.group.addButton(btn, self.button_id[key])

    def select_default(self):
        pass

    def getSelection(self):
        selection = None

        if self.button_type == 'radio':
            selection = self.group.checkedId()
        elif self.button_type == 'check':
            selection = []

            for btn in self.group.buttons():
                if btn.isChecked():
                    selection.append(btn.text())

        return selection

class EntityScope(ScopeBox):
    title = "Action scope"
    button_type = 'radio'

    def populate_button_id(self):
        self.button_id = {
            '1 - everything': 0,
            '2 - entity': 1,
            '3 - instance': 2,
        }

    def select_default(self):
        self.group.button(2).setChecked(True)

class CompilerScope(ScopeBox):
    title = "Compilers"
    button_type = 'check'

    def populate_button_id(self):
        options = CompilerOptions()

        self.button_id = {}

        for i in range(len(options.compilers_list)):
            compiler = options.compilers_list[i]
            self.button_id[compiler.name] = i

    def select_default(self):
        for btn in self.group.buttons():
            if btn.text() == 'clang':
                btn.setChecked(True)

class OptimisationScope(ScopeBox):
    title = "Optimisations"
    button_type = 'check'

    def populate_button_id(self):
        options = CompilerOptions()

        self.button_id = {}

        for (idx, level) in enumerate(options.optim_levels_list):
            self.button_id[level] = idx

    def select_default(self):
        pass

class ActionsScope(QWidget):
    def __init__(self):
        super().__init__()

        self.build_layout()

    def build_layout(self):
        self.layout = QGridLayout()
        self.setLayout(self.layout)

        self.entity_scope = EntityScope()
        self.compiler_scope = CompilerScope()
        self.optimisation_scope = OptimisationScope()

        self.layout.addWidget(self.entity_scope, 0, 0, 1, 2)
        self.layout.addWidget(self.compiler_scope, 1, 0, 1, 1)
        self.layout.addWidget(self.optimisation_scope, 1, 1, 1, 1)

    def get_scopes(self):
        scopes = {}

        scopes['entity'] = self.entity_scope.getSelection()
        scopes['compiler'] = self.compiler_scope.getSelection()
        scopes['optimisation'] = self.optimisation_scope.getSelection()

        return scopes

class ActionButton(QWidget):
    def __init__(self, action):
        super().__init__()

        self.action = action
        self.build_layout()


    def build_layout(self):
        self.layout = QHBoxLayout(self)
        self.checkbox = QCheckBox(self)

        self.button = QToolButton()
        self.button.setDefaultAction(self.action)
        self.button.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Maximum)

        self.layout.addWidget(self.checkbox)
        self.layout.addWidget(self.button)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(self.layout)


class ActionsPane(QWidget):
    def __init__(self):
        super().__init__()

        self.group = QButtonGroup()
        self.group.setExclusive(False)

        self.scope_widget = ActionsScope()
        self.action_buttons = QVBoxLayout()
        self.big_red_button = QPushButton("Automate !!!", clicked=self.automate)
        self.big_red_button.setStyleSheet("QPushButton { background-color : red}")

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.layout.addWidget(self.scope_widget)
        self.layout.addLayout(self.action_buttons)
        self.layout.addStretch()
        self.layout.addWidget(self.big_red_button)

    def registerAction(self, action):
        button = ActionButton(action)
        self.group.addButton(button.checkbox)
        self.action_buttons.addWidget(button)

    def getCheckedActions(self):
        return [btn.parent().action for btn in self.group.buttons() if btn.isChecked()]

    def automate(self, event):
        for action in self.getCheckedActions():
            action.triggerIt()

class EntityManagerView(QListView):
    entitySelectionChanged = pyqtSignal(Entity)

    def __init__(self, manager):
        super().__init__()
        self.manager_model = EntityManagerListModel(manager)
        self.setModel(self.manager_model)

    def selectionChanged(self, selected, deselected):
        super().selectionChanged(selected, deselected)
        idx = selected.indexes()[0].row()
        entity = self.model().manager.entityList[idx]
        self.entitySelectionChanged.emit(entity)

    def refresh(self):
        index = self.selectionModel().currentIndex()
        self.manager_model.endResetModel()
        self.selectionModel().select(index, QItemSelectionModel.Select)

class EntityView(QTableView):
    instanceSelectionChanged = pyqtSignal(EntityInstance)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.entity_model = EntityTableModel()
        self.setModel(self.entity_model)

        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.horizontalHeader().setResizeMode(QHeaderView.Stretch)
        self.verticalHeader().setResizeMode(QHeaderView.Stretch)

    @pyqtSlot(Entity)
    def entitySelectionChanged(self, entity):
        self.entity = entity
        self.entity_model.setEntity(entity)


    def selectionChanged(self, selected, deselected):
        super().selectionChanged(selected, deselected)

        idx = selected.indexes()[0]
        instance = self.entity_model.getInstanceAt(idx.row(), idx.column())

        self.instanceSelectionChanged.emit(instance)

    def refresh(self):
        index = self.selectionModel().currentIndex()
        self.entity_model.endResetModel()
        self.selectionModel().select(index, QItemSelectionModel.Select)

    def selectInstanceType(self, instance_type):
        (compiler, opt_level) = instance_type

        row = None
        col = None

        options = CompilerOptions()
        optim_levels = options.optim_levels_list
        compiler_names = sorted( [compiler.name for compiler in options.compilers_list] )

        try:
            row = compiler_names.index(compiler)
            col = optim_levels.index(opt_level)

            idx = self.model().index(row, col)
            self.selectionModel().select(idx, QItemSelectionModel.Select)
        except:
            raise Exception("Can't autoselect such instance")

class InstanceView(QTabWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.instance = None
        self.last_selected_tab = None
        self.currentChanged.connect(self.set_recent_tab)
        self.widgets = {}

    def build_layout(self):
        self.clear()
        factory = ResultWidgetFactory()

        self.widgets = {}
        self.create_legacy_tab()
        for result in self.instance.results.values():
            idx = self.addTab(factory.get_widget(result), result.tag)
            self.widgets[result.tag] = idx

    def create_legacy_tab(self):
        self.legacy_report_widget = LegacyResultReportWidget(self.instance)
        idx = self.addTab(self.legacy_report_widget, "Legacy report")
        self.widgets["Legacy report"] = idx

    def setInstance(self, instance):
        self.instance = instance
        self.refresh()

    def refresh(self):
        if self.instance is None:
            return

        self.currentChanged.disconnect(self.set_recent_tab)
        self.build_layout()
        self.currentChanged.connect(self.set_recent_tab)

        self.select_recent_tab()

    def select_recent_tab(self):
        try:
            if self.last_selected_tab is None:
                self.setCurrentIndex(self.widgets["Legacy report"])
            else:
                self.setCurrentIndex(self.widgets[self.last_selected_tab])
        except Exception as e:
            print(e)

    @pyqtSlot(int)
    def set_recent_tab(self, idx):
        try:
            w = self.currentWidget()
            tag = w.result.tag
            self.last_selected_tab = tag
        except Exception as e:
            print(e)
