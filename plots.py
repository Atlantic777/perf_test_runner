from PyQt4.QtCore import Qt
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class MyPlot(FigureCanvas):
    def __init__(self, model, table=None):
        self.table = table
        self.model = model
        self.selection = None

        self.create_labels()
        self.x_values = range(len(self.x_labels))

        self.fig = Figure()
        super().__init__(self.fig)
        self.axes = self.fig.add_subplot(111)

        self.draw_data()
        self.connect_signals()
        self.setup_axis_ticks()

    def setup_axis_ticks(self):
        x_axis = self.axes.get_xaxis()
        x_axis.set_ticks(self.x_values)
        x_axis.set_ticklabels(self.x_labels)

    def selection_changed(self, selected, deselected):
        pass

    def sorting_changed(self, selected, deselected):
        pass

    def connect_signals(self):
        self.model.modelReset.connect(self.sorting_changed)

        if self.table:
            selection_model = self.table.selectionModel()
            selection_model.selectionChanged.connect(self.selection_changed)

    def create_labels(self):
        cols = self.model.get_plotable_cols()
        self.x_labels = [col[0] for col in cols]

class MyOverviewPlot(MyPlot):
    def draw_data(self):
        self.axes.clear()

        for row in range(self.model.rowCount()):
            d = []
            values = self.model.getInstanceAt(row)

            for col in self.x_labels:
                d.append(values[col])

            d = np.array(d)

            self.axes.plot(self.x_values, d, 'b')

        self.axes.set_ylim(0, 1)
        self.draw()

class MySinglePlot(MyPlot):
    def draw_data(self):
        self.axes.clear()

        if self.selection is None:
            return

        values = self.selection

        d = []

        for col in self.x_labels:
            d.append(values[col])

        d = np.array(d)

        self.axes.plot(self.x_values, d, 'b')
        x_axis = self.axes.get_xaxis()
        x_axis.set_ticks(self.x_values)
        x_axis.set_ticklabels(self.x_labels)

        self.axes.set_ylim(0, 1)
        self.draw()

    def selection_changed(self, selected, deselected):
        try:
            idx = selected.indexes()[0]
            self.selection = self.model.getInstanceAt(idx.row())
            self.draw_data()
        except Exception as e:
            print("something bad with selection")
            print(e)
            self.selection = None
