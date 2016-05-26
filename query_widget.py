from PyQt4.QtGui import *
from PyQt4.QtCore import (
    Qt,
    pyqtSlot,
    pyqtSignal,
)

from query import *
from plots import *

class QueryPlotWidgetBuilder:
    def __init__(self):
        self.d = {}

        # self.d[PerfQuery] = [
        #     PerfIPCOverviewPlot,
        #     PerfIPCSingleItemPlot,
        # ]

        # self.d[ExecTimeQuery] = [
        #     ExecTimeOverviewPlot,
        #     ExecTimeSinglePlot,
        # ]

        # self.d[ExecSizeQuery] = [
        #     ExecSizeOverviewPlot,
        #     ExecSizeSinglePlot,
        # ]

        # self.d[ExecTimeNormQuery] = [
        #     ExecTimeNormOverviewPlot,
        #     ExecTimeNormSinglePlot,
        # ]

    def get_widget(self, query, table):
        if type(query) not in self.d:
            return QWidget()

        w = QWidget()
        l = QVBoxLayout()
        w.setLayout(l)

        plot_list = self.d[type(query)]
        for PlotClass in plot_list:
            l.addWidget(PlotClass(table.model(), table))

        return w

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
        self.table.model().modelReset.connect(self.should_redraw_plots)

        w = self.get_plot_list_widget()
        self.scrollable.setWidget(w)

    def should_redraw_plots(self):
        print("should replot")

    def get_plot_list_widget(self):
        w = QueryPlotWidgetBuilder().get_widget(self.query, self.table)
        return w
