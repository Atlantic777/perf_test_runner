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
        self.extract_data()

    def strip_header(self):
        self.raw_results = self.raw_results.split('\n')
        self.raw_results = self.raw_results[3:]

    def extract_data(self):
        stripped_rows = []
        for row in self.raw_results:
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

class TimeExecutionParser:
    columns = [
        'user',
        'system',
        'elapsed',
        'CPU',
        'pagefaults',
    ]

    def __init__(self, raw_results=None):
        if raw_results is None:
            return False

        self.values = {}

        self.raw_results = raw_results
        self.raw_results_ref = raw_results

        self.parse()

    def parse(self):
        self.strip_header()
        self.extract_data()

    def strip_header(self):
        pass

    def extract_data(self):
        splitted_cols = self.raw_results.split(' ')

        try:
            for tag in self.columns:
                for item in splitted_cols:
                    if tag in item:
                        value = item.strip(tag)

                        try:
                            value = float(value)
                        except:
                            pass

                        self.values[tag] = value
        except Exception as e:
            print(e)

class ExecutableSizeParser:
    columns = [
        'text',
        'data',
        'bss',
        'dec',
    ]

    def __init__(self, raw_results=None):
        if raw_results is None:
            return False

        self.values = {}

        self.raw_results = raw_results
        self.raw_results_ref = raw_results

        self.parse()

    def parse(self):
        self.strip_header()
        self.extract_data()

    def strip_header(self):
        pass

    def extract_data(self):
        self.raw_results = self.raw_results.replace(' ', '')
        splitted_rows = self.raw_results.split('\n')
        column_names = splitted_rows[0].split('\t')
        column_values = splitted_rows[1].split('\t')

        try:
            for tag in self.columns:
                idx  = column_names.index(tag)
                val = column_values[idx]

                try:
                    val = int(val)
                except:
                    pass

                self.values[tag] = val
        except Exception as e:
            print(e)
            print(self.raw_results)
            print(splitted_rows)
            print(column_names)
            print(column_values)

class PerfEstParser:
    columns = [
        'estimation',
    ]

    def __init__(self, raw_results=None):
        if raw_results is None:
            return False

        self.values = {}
        self.values['freq'] = {}

        self.raw_results = raw_results
        self.raw_resutls_ref = raw_results

        self.parse()

    def parse(self):
        self.strip_header()
        self.extract_data()

    def strip_header(self):
        pass

    def extract_data(self):
        lines = self.raw_results.split('\n')
        freq_dict = self.values['freq']

        for l in lines:
            if 'perf_est_front' in l:
                s = l.split(',')[1:]

                function = s[0]

                d = {}
                block_name = s[1]
                d['entry_freq'] = s[2]
                d['block_freq'] = s[3]
                d['norm_freq']= s[4]
                d['cnt'] = s[5]
                d['val'] = s[6]

                if function not in freq_dict:
                    freq_dict[function] = {}

                freq_dict[function][block_name] = d
            elif "Total sum" in l:
                s = l.split(':')
                val = float( s[1] )
                self.values[self.columns[0]] = val

class PerfEstBackParser:
    columns = [
        'total',
    ]

    def __init__(self, raw_results=None):
        if raw_results is None:
            return False

        self.values = {}
        self.values['freq'] = {}

        self.raw_results = raw_results
        self.raw_results_ref = raw_results

        self.parse()

    def parse(self):
        self.strip_header()
        self.extract_data()

    def strip_header(self):
        pass

    def extract_data(self):
        lines = self.raw_results.split('\n')
        freq_dict = self.values['freq']

        for l in lines:
            if 'perf_est_back' in l:
                s = l.split(',')[1:]

                function = s[0]

                d = {}
                block_name = s[1]
                d['entry_freq'] = s[2]
                d['block_freq'] = s[3]
                d['norm_freq']= s[4]
                d['cnt'] = s[5]
                d['val'] = s[6]

                if function not in freq_dict:
                    freq_dict[function] = {}

                freq_dict[function][block_name] = d
            elif 'final' in l:
                val = l.split(':')[1]
                val = float(val)

                self.values[self.columns[0]] = val
                return
