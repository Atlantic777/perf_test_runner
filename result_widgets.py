from PyQt4.QtGui import (
    QTextBrowser,
    QFont,
)

from results import *

class QMonoFont(QFont):
    def __init__(self):
        super().__init__()

        self.setFamily('monospace')
        self.setFixedPitch(True)
        self.setStyleHint(QFont.TypeWriter)


class ResultWidgetFactory:
    result2widget_map = {}

    def get_widget(self, result):
        t = type(result)
        WidgetClass = None

        try:
            WidgetClass = self.result2widget_map[t]
        except:
            WidgetClass = DefaultResultWidget

        return WidgetClass(result)

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


