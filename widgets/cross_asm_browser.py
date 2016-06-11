from PyQt4.QtGui import *
from PyQt4.QtCore import (
    Qt,
)

from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter

class CrossAsmBrowser(QSplitter):
    def __init__(self, result, parent=None):
        super().__init__(parent=parent)

        self.result = result
        self.result.parse()

        self.parsed_asm = result.parsed_output['asm_fbb_tree']

        self.build_layout()
        self.set_models()
        self.connect_signals()

        self.setStretchFactor(1, 2)

    def build_layout(self):
        # we need vertical splitter
        self.setOrientation(Qt.Horizontal)

        # left side is horizontally splitted
        self.leftSide = QSplitter(self)
        self.leftSide.setOrientation(Qt.Vertical)

        # on left side there are function, bb choser and counter label
        self.function_choser = QListView(self.leftSide)
        self.bb_choser = QListView(self.leftSide)
        self.total_sum = QLabel("<b>Total sum: </b>")

        self.leftSide.addWidget(self.function_choser)
        self.leftSide.addWidget(self.bb_choser)
        self.leftSide.addWidget(self.total_sum)
        self.addWidget(self.leftSide)

        # on the right side is text area (colored?!)
        self.text_browser = QTextBrowser(self)
        self.addWidget(self.text_browser)

    def set_models(self):
        self.functions_model = QStringListModel()
        self.functions = sorted(list(self.parsed_asm.keys()))
        self.functions_model.setStringList(self.functions)

        self.bb_model = QStringListModel()

        self.function_choser.setModel(self.functions_model)
        self.bb_choser.setModel(self.bb_model)

    def connect_signals(self):
        # when function selection changes, update bb list
        self.function_choser.selectionModel().currentChanged.connect(self.function_changed)

        # when bb list selection changes, update text area
        self.bb_choser.selectionModel().currentChanged.connect(self.bb_changed)

        # when text area changes, clear cnt label
        self.text_browser.selectionChanged.connect(self.selection_changed)
        # when text area selection changes, trigger counting
        # when counting is triggered, cnt label should be updated

    def function_changed(self, selected, deselected):
        function_name = self.functions_model.stringList()[selected.row()]
        self.current_fn = function_name

        self.bb_model.setStringList(sorted(list(self.parsed_asm[function_name].keys())))
        self.set_bb(0)

    def bb_changed(self, selected, deselected):
        self.set_bb(selected.row())

    def set_bb(self, row):
        bb_name = self.bb_model.stringList()[row]
        self.current_bb = bb_name

        bb_content = self.parsed_asm[self.current_fn][bb_name]
        bb_content = "\n".join(bb_content)

        Lexer = get_lexer_by_name('asm')
        s = highlight(bb_content, Lexer, HtmlFormatter(noclasses=True))

        self.text_browser.setText(s)

    def selection_changed(self):
        cursor = self.text_browser.textCursor()
        selection = cursor.selection().toPlainText()

        count = selection.count('\n') + 1

        self.total_sum.setText("<b>Total sum:</b> {}".format(count))
