from PyQt4.QtGui import (
    QListView,
    QWidget,
    QLabel,
    QVBoxLayout,
    QTableView,
    QAbstractItemView,
    QTextBrowser,
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
        report = "Hello world!\n"

        try:
            report += self.instance.results['bitcode_path']
        except:
            pass


        return report
