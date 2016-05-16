from PyQt4.QtGui import (
    QSplitter,
)

from PyQt4.QtCore import (
    Qt,
)

from . import (
    QueryListView,
    QueryDataView,
)

class QueryExplorer(QSplitter):
    def __init__(self, entity_manager):
        super().__init__(Qt.Horizontal)
        self.entity_manager = entity_manager

        self.build_layout()

    def build_layout(self):
        pass

