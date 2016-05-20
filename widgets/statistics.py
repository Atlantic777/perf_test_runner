from PyQt4.QtGui import *
from PyQt4.QtCore import (
    Qt,
    pyqtSlot,
    pyqtSignal,
)

from query import *

class QueryListView(QListView):
    query_changed = pyqtSignal(Query)

    def __init__(self, parent):
        super().__init__(parent)

        self.entity_manager = self.parent().entity_manager
        self.query_manager = QueryManager(self)

        titles = self.query_manager.get_titles()
        model = QStringListModel(titles)

        self.setModel(model)


    def selectionChanged(self, selected, deselected):
        super().selectionChanged(selected, deselected)

        title = selected.indexes()[0].data()
        idx = selected.indexes()[0].row()

        query = self.query_manager.get(title)
        self.query_changed.emit(query)

class QueryDataTableView(QTableView):
    def __init__(self):
        super().__init__()
        self.setSortingEnabled(True)
        self.horizontalHeader().setResizeMode(QHeaderView.ResizeToContents)

class QueryExplorer(QSplitter):
    def __init__(self, entity_manager):
        super().__init__(Qt.Horizontal)
        self.entity_manager = entity_manager

        self.build_layout()
        self.setSizes([250, 1050])

        self.connect_signals()

    def build_layout(self):
        self.query_list = QueryListView(self)
        self.query_data = QueryDataTableView()

        self.addWidget(self.query_list)
        self.addWidget(self.query_data)

    def connect_signals(self):
        self.query_list.query_changed.connect(self.on_query_changed)

    @pyqtSlot(Query)
    def on_query_changed(self, query):
        model = query.get_model()
        self.query_data.setModel(model)
