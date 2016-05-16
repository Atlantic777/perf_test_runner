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

class ActionsScope(QGroupBox):
    title = "Action scope"
    button_id = {
        '1 - everything': 0,
        '2 - entity': 1,
        '3 - instance': 2,
    }

    def __init__(self):
        super().__init__(title=self.title)

        self.group = QButtonGroup()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        keys = list(self.button_id.keys())
        keys.sort()

        for key in keys:
            btn = QRadioButton(key)
            self.layout.addWidget(btn)
            self.group.addButton(btn, self.button_id[key])

        self.group.button(2).setChecked(True)

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


class InstanceView(QWidget):
    instance = None

    def __init__(self, parent=None):
        super().__init__(parent)
        self.build_layout()

    def build_layout(self):
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.browser = QTextBrowser()

        font = QFont()
        font.setFamily('monospace')
        font.setFixedPitch(True)
        font.setStyleHint(QFont.TypeWriter)

        self.browser.setCurrentFont(font)
        self.layout.addWidget(self.browser)

    def setInstance(self, instance):
        self.instance = instance
        self.refresh()

    def refresh(self):
        if self.instance is None:
            return

        report = self.generate_report()
        self.browser.setText(report)

    def generate_report(self):
        result_types = [
            CompilationResult,
            GenerateBitcodeResult,
            OptimiserStatsResult,
            PerfResult,
            ExecutableSizeResult,
            TimeExecutionResult,
        ]

        report = ""

        for t in [res.tag for res in result_types]:
            try:
                result = self.instance.results[t]

                if result.action_output_file:
                    report += result.action_output_file.full_path + '\n'
                    report += "-"*10 + '\n'

                if result.analysis_output_file:
                   with open(result.analysis_output_file.full_path, "r")  as f:
                        report += f.read() + '\n'
                        report += "-"*10 + '\n'

            except Exception as e:
                pass

        return report

class OptimStatsView(QTableView):
    raw_report = None

    def __init__(self, parent=None):
        super().__init__(parent)
        # self.stats_model = OptimStatsModel(raw)

    def setStatsReport(self, report):
        self.raw_report = report
