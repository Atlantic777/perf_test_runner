"""
QWidgets for representing models of raw data
"""
from PyQt4.QtGui import (
    QListView,
    QWidget,
    QLabel,
    QVBoxLayout,
    QTableView,
    QAbstractItemView,
    QTextBrowser,
    QFont,
    QToolButton,
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
        self.entity_model.endResetModel()


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
