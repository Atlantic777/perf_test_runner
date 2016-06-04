from PyQt4.QtGui import *

from results import *
from models import *

class QMonoFont(QFont):
    def __init__(self):
        super().__init__()

        self.setFamily('monospace')
        self.setFixedPitch(True)
        self.setStyleHint(QFont.TypeWriter)

class DefaultResultWidget(QTextBrowser):
    def __init__(self, result):
        super().__init__()

        self.result = result
        self.set_font()
        self.set_report()

    def set_font(self):
        font = QFont()
        font.setFamily('monospace')
        font.setFixedPitch(True)
        font.setStyleHint(QFont.TypeWriter)
        self.setCurrentFont(font)

    def set_report(self):
        report = self.result.generate_report()
        self.setText(report)

class LegacyResultReportWidget(QTextBrowser):
    def __init__(self, instance):
        super().__init__()

        self.instance = instance

        font = QMonoFont()
        self.setFont(font)

        report = self.generate_report()
        self.setText(report)

    def generate_report(self):
        report = ""

        keys = list(self.instance.results.keys())
        keys.sort()

        results = self.instance.results

        for result_tag in keys:
            report += results[result_tag].generate_report()

        return report

class PerfEstWidget(QWidget):
    def __init__(self, result, parent=None):
        super().__init__(parent=parent)
        self.result = result
        self.result.parse()
        self.build_layout()

    def build_layout(self):
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.add_total_sum_qlabel()
        self.add_table()

    def add_total_sum_qlabel(self):
        total_sum_tag = self.result.ParserClass.columns[0]
        val = float(self.result.parsed_data[total_sum_tag])
        s = "{:,.2f}".format(val)
        self.layout.addWidget(QLabel("<b>Total sum: " + s + "</b>"))

    def add_table(self):
        self.table = QTableView()
        self.model = PerfEstModel(self.result)
        self.table.setModel(self.model)

        self.layout.addWidget(self.table)

class ResultWidgetFactory:
    result2widget_map = {
        PerfEstResult : PerfEstWidget,
        PerfEstBackResult : PerfEstWidget,
    }

    def get_widget(self, result):
        t = type(result)
        WidgetClass = None

        try:
            WidgetClass = self.result2widget_map[t]
        except:
            WidgetClass = DefaultResultWidget

        return WidgetClass(result)
