from results import *

class ResultParserBase:
    columns = None

    def __init__(self, raw_results):
        self._preinit(raw_results)
        self.parse()

    def _preinit(self, raw_results):
        self.values = {}
        self.raw_results = raw_results
        self.raw_results_ref = raw_results

    def parse(self):
        self.strip_header()
        self.extract_data()

    def strip_header(self):
        pass

    def extract_data(self):
        pass

class PerfResultParser(ResultParserBase):
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

class TimeExecutionParser(ResultParserBase):
    columns = [
        'user',
        'system',
        'elapsed',
        'CPU',
        'pagefaults',
    ]

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

class ExecutableSizeParser(ResultParserBase):
    columns = [
        'text',
        'data',
        'bss',
        'dec',
    ]

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

class PerfEstParser(ResultParserBase):
    columns = [
        'estimation',
    ]

    def __init__(self, raw_results):
        super()._preinit(raw_results)
        self.values['freq'] = {}
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

class PerfEstBackParser(ResultParserBase):
    columns = [
        'total',
    ]

    def __init__(self, raw_results):
        super()._preinit(raw_results)
        self.values['freq'] = {}
        self.parse()

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

class CrossAsmParser(ResultParserBase):
    def extract_data(self):
        asm_fbb_tree = {}
        self.values['asm_fbb_tree'] = asm_fbb_tree

        current_func = None
        current_bb = None
        current_l = None

        for l in self.raw_results.split('\n'):
            if "# @" in l and l[0] != '\t':
                func_name = l.split(':')[0]
                asm_fbb_tree[func_name] = {}
                current_func = func_name
            elif "# %" in l:
                bb_name = l.split('# %')[1][:-1]
                l = []
                asm_fbb_tree[current_func][bb_name] = l
                current_bb = bb_name
                current_l = l
            elif current_func and current_bb:
                current_l.append(l[:-1])
                pass
            else:
                pass

