from PyQt4.QtGui import (
    QListView,
    QWidget,
    QLabel,
    QVBoxLayout,
    QTableView,
    QAbstractItemView,
)
from PyQt4.QtCore import (
    pyqtSlot,
    pyqtSignal,
)

from entity import Entity
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
    def __init__(self, parent=None):
        super().__init__(parent)

        self.entity_model = EntityTableModel()
        self.setModel(self.entity_model)

        self.setSelectionBehavior(QAbstractItemView.SelectRows)

    @pyqtSlot(Entity)
    def entitySelectionChanged(self, entity):
        self.entity = entity
        self.entity_model.setEntity(entity)
