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

class EntityDetailWidget(QWidget):
    def __init__(self, entity):
        super().__init__()
        self.resize(1920/2, 600)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.detail_view = self._EntityDetailWidget(entity)
        self.layout.addWidget(QLabel(entity.source.name))
        self.layout.addWidget(self.detail_view)

        self.setWindowTitle("# " + entity.source.name)

    class _EntityDetailWidget(EntityWidget):
        def __init__(self, entity):
            super().__init__()

            w = self
            w.entity_view.entitySelectionChanged(entity)

            instance_changed = w.entity_view.instanceSelectionChanged
            instance_changed.connect(w.instance_view.setInstance)

            sh = w.entity_view.minimumSizeHint().height()
            h = self.size().height()

            self.setSizes([sh, h-sh])


class QueryDataTableView(QTableView):
    def __init__(self):
        super().__init__()
        self.setSortingEnabled(True)
        self.horizontalHeader().setResizeMode(QHeaderView.ResizeToContents)
        self.verticalHeader().setVisible(False)

        self.doubleClicked.connect(self.open_details)

        self.detail_views = []

    def open_details(self, index):
        row = index.row()
        col = index.column()

        entity = self.model().getEntityAt(row)

        w  = EntityDetailWidget(entity)
        self.detail_views.append(w)
        w.show()

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
