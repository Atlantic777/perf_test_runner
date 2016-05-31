from . import Application

from widgets import (
    ResultExplorer,
    QueryExplorer,
)

from PyQt4.QtGui import (
    QApplication,
    QTabWidget,
)

from PyQt4.QtCore import (
    QObject,
)

from models import EntityManagerListModel
from entity import *
from actions import *

class GUIApplication(Application, QObject):
    selected_instance = None
    selected_entity = None

    def __init__(self):
        super(Application, self).__init__()
        super(QObject, self).__init__()

        self.qApp = QApplication([])

        # init main window widget
        self.w = QTabWidget()
        self.w.resize(1300, 700)
        self.w.setWindowTitle("# Hello world!")

        # other init routines
        self.entity_manager = EntityManager()
        self.build_layout()
        self.prepare_result_dirs()

        self.w.show()

    def prepare_result_dirs(self):
        options = CompilerOptions()

        try:
            for d in options.get_output_dirs():
                makedirs(path.join(OUTPUT_ROOT, d))
        except:
            pass

    def run(self):
        self.qApp.exec_()

    def build_layout(self):
        self.result_explorer = ResultExplorer(self.entity_manager)
        self.w.addTab(self.result_explorer, "Result explorer")

        self.query_explorer = QueryExplorer(self.entity_manager)
        self.w.addTab(self.query_explorer, "Queries")
