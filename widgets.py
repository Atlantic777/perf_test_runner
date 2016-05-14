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

        # self.setSelectionBehavior(QAbstractItemView.SelectRows)
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
            'bitcode_path',
            'opt_stats',
        ]

        report = ""

        for t in result_types:
            try:
                report += self.instance.results[t] + '\n'
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
