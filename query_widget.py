from PyQt4.QtGui import *
from PyQt4.QtCore import (
    Qt,
    pyqtSlot,
    pyqtSignal,
)

from query import *
from plots import *

from widgets.result_explorer import EntityWidget

class QueryPlotWidgetBuilder:
    def get_widget(self, query, table):
        w = QWidget()
        l = QVBoxLayout()
        w.setLayout(l)

        plot_list = [MyOverviewPlot, MySinglePlot]
        for PlotClass in plot_list:
            l.addWidget(PlotClass(table.model(), table))

        return w

class QueryDataTableView(QTableView):
    def __init__(self):
        super().__init__()
        self.setSortingEnabled(True)
        self.horizontalHeader().setResizeMode(QHeaderView.ResizeToContents)
        self.verticalHeader().setVisible(False)

        self.doubleClicked.connect(self.open_details)

    def open_details(self, index):
        row = index.row()
        col = index.column()
        print( (row, col) )

        entity = self.model().getEntityAt(row)
        print(entity)

        w  = EntityWidget(parent=None)
        self.w = w
        w.entity_view.entitySelectionChanged(entity)

        instance_changed = w.entity_view.instanceSelectionChanged
        instance_changed.connect(w.instance_view.setInstance)

        w.show()
        print("end of this")



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
