from PyQt4.QtGui import *
from PyQt4.QtCore import (
    Qt,
    pyqtSlot,
    pyqtSignal,
)

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

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
        self.verticalHeader().setVisible(False)

class QueryWidget(QSplitter):
    def __init__(self, parent):
        super().__init__(parent)
        self.setOrientation(Qt.Horizontal)

        self.query = None

        self.table = QueryDataTableView()

        self.scrollable = QScrollArea()
        self.addWidget(self.table)
        self.addWidget(self.scrollable)

    def set_query(self, query):
        self.query = query

        self.table.setModel(self.query.get_model())

        w = self.get_plot_list_widget()
        self.scrollable.setWidget(w)

    def get_plot_list_widget(self):
        w = QWidget()
        l = QVBoxLayout()
        w.setLayout(l)

        plot_list = self.query.get_plots()
        for plot in plot_list:
            l.addWidget(plot)

        return w

class QueryExplorer(QSplitter):
    def __init__(self, entity_manager):
        super().__init__(Qt.Horizontal)
        self.entity_manager = entity_manager

        self.build_layout()
        self.setSizes([250, 1050])

        self.connect_signals()

    def build_layout(self):
        self.query_list = QueryListView(self)
        self.query_widget = QueryWidget(self)
        self.query_data = self.query_widget.table

        self.addWidget(self.query_list)
        self.addWidget(self.query_widget)

    def connect_signals(self):
        self.query_list.query_changed.connect(self.on_query_changed)

    @pyqtSlot(Query)
    def on_query_changed(self, query):
        self.query_widget.set_query(query)
