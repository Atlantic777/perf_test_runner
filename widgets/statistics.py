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

class QueryWidget(QSplitter):
    def __init__(self, parent):
        super().__init__(parent)
        self.setOrientation(Qt.Vertical)

        p = parent
        self.fig = Figure()
        self.axes = self.fig.add_subplot(111)

        self.table = QueryDataTableView()
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(p)

        self.addWidget(self.table)
        self.addWidget(self.canvas)

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
        self.current_query = query
        model = query.get_model()
        self.query_data.setModel(model)

        self.show_plot()

    def show_plot(self):
        arrays = []
        query_data = self.current_query.query_data
        columns = self.current_query.columns

        axes = self.query_widget.axes
        canvas = self.query_widget.canvas

        # construct list of 4-value arrays
        for entity_title in query_data:
            d = []

            for (col_title, function) in columns:
                d.append(query_data[entity_title][col_title])

            d = np.array(d)
            d = np.max(d) / d

            axes.plot([0, 1, 2, 3], d, 'r')

        canvas.draw()
