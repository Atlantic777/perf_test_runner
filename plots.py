from PyQt4.QtCore import Qt
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class PerfIPCOverviewPlot(FigureCanvas):
    def __init__(self, model, table=None):
        self.fig = Figure()
        super().__init__(self.fig)
        self.axes = self.fig.add_subplot(111)

        self.table = table
        self.model = model

        self.x_labels = [
            '-O0 IPC',
            '-O1 IPC',
            '-O2 IPC',
            '-O3 IPC',
        ]
        self.x_values = range(len(self.x_labels))


        self.draw_data()
        self.connect_signals()

        x_axis = self.axes.get_xaxis()
        x_axis.set_ticks(self.x_values)
        x_axis.set_ticklabels(self.x_labels)

    def connect_signals(self):
        self.model.modelReset.connect(self.sorting_changed)

        if self.table:
            selection_model = self.table.selectionModel()
            selection_model.selectionChanged.connect(self.selection_changed)

    def draw_data(self):
        self.axes.clear()

        for row in range(self.model.rowCount()):
            d = []
            values = self.model.getInstanceAt(row)

            for col in self.x_labels:
                d.append(values[col])

            d = np.array(d)

            self.axes.plot(self.x_values, d, 'b')

    def selection_changed(self, selected, deselected):
        print("selection changed")
        pass

    def sorting_changed(self, selected, deselected):
        print("sorting changed")
        pass

class PerfIPCSingleItemPlot(FigureCanvas):
    def __init__(self, model, table=None):
        self.fig = Figure()
        super().__init__(self.fig)
        self.axes = self.fig.add_subplot(111)

        self.table = table
        self.model = model

        self.x_labels = [
            '-O0 IPC',
            '-O1 IPC',
            '-O2 IPC',
            '-O3 IPC',
        ]
        self.x_values = range(len(self.x_labels))


        self.selection = None

        self.draw_data()
        self.connect_signals()

    def connect_signals(self):
        self.model.modelReset.connect(self.sorting_changed)

        if self.table:
            selection_model = self.table.selectionModel()
            selection_model.selectionChanged.connect(self.selection_changed)

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

        self.draw()


    def selection_changed(self, selected, deselected):
        print("selection changed")

        try:
            idx = selected.indexes()[0]
            self.selection = self.model.getInstanceAt(idx.row())
            self.draw_data()
        except Exception as e:
            print("something bad with selection")
            print(e)
            self.selection = None


    def sorting_changed(self, selected, deselected):
        print("sorting changed")
        pass

class ExecTimeOverviewPlot(FigureCanvas):
    def __init__(self, model, table=None):
        self.fig = Figure()
        super().__init__(self.fig)
        self.axes = self.fig.add_subplot(111)

        self.table = table
        self.model = model

        self.x_labels = [
            '-O0 dec',
            '-O1 dec',
            '-O2 dec',
            '-O3 dec',
        ]
        self.x_values = range(len(self.x_labels))

        self.draw_data()
        self.connect_signals()

        x_axis = self.axes.get_xaxis()
        x_axis.set_ticks(self.x_values)
        x_axis.set_ticklabels(self.x_labels)

    def connect_signals(self):
        self.model.modelReset.connect(self.sorting_changed)

        if self.table:
            selection_model = self.table.selectionModel()
            selection_model.selectionChanged.connect(self.selection_changed)

    def draw_data(self):
        self.axes.clear()

        for row in range(self.model.rowCount()):
            d = []
            values = self.model.getInstanceAt(row)

            for col in self.x_labels:
                d.append(values[col])

            d = np.array(d)

            self.axes.plot(self.x_values, d, 'b')

    def selection_changed(self, selected, deselected):
        print("selection changed")
        pass

    def sorting_changed(self, selected, deselected):
        print("sorting changed")
        pass

class ExecTimeSingleItemPlot(FigureCanvas):
    def __init__(self, model, table=None):
        self.fig = Figure()
        super().__init__(self.fig)
        self.axes = self.fig.add_subplot(111)

        self.table = table
        self.model = model

        self.x_labels = [
            '-O0 dec',
            '-O1 dec',
            '-O2 dec',
            '-O3 dec',
        ]
        self.x_values = range(len(self.x_labels))


        self.selection = None

        self.draw_data()
        self.connect_signals()

    def connect_signals(self):
        self.model.modelReset.connect(self.sorting_changed)

        if self.table:
            selection_model = self.table.selectionModel()
            selection_model.selectionChanged.connect(self.selection_changed)

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

        self.draw()


    def selection_changed(self, selected, deselected):
        print("selection changed")

        try:
            idx = selected.indexes()[0]
            self.selection = self.model.getInstanceAt(idx.row())
            self.draw_data()
        except Exception as e:
            print("something bad with selection")
            print(e)
            self.selection = None


    def sorting_changed(self, selected, deselected):
        print("sorting changed")
        pass
