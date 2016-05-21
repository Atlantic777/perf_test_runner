from results import *

class PerfResultParser:
    columns = [
        'task-clock',
        'context-switches',
        'cpu-migrations',
        'page-faults',
        'cycles',
        'stalled-cycles-frontend',
        'stalled-cycles-backend',
        'instructions',
        'branches',
        'branch-misses',
        'time',
    ]

    def __init__(self, raw_results=None):
        if raw_results is None:
            return False

        self.values = {}

        self.raw_results = raw_results # working copy
        self.raw_results_ref = raw_results # reference to original object

        self.parse()

    def parse(self):
        self.strip_header()

    def strip_header(self):
        self.raw_results = self.raw_results.split('\n')

        stripped_rows = []

        for row in self.raw_results[3:]:
            broken = row.split('#')[0]
            broken = broken.strip(' ')

            if len(broken) > 0:
                stripped_rows.append(broken)
            else:
                pass

        try:
            for tag in self.columns:
                for row in stripped_rows:
                    if tag == row.split(' ')[-1]:
                        value = row.split(' ')[0].replace(',', '')
                        if '.' in value:
                            value = float(value)
                        else:
                            value = int(value)

                        self.values[tag] = value
        except:
            # print("can't parse " + tag)
            pass
