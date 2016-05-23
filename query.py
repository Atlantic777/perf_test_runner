from PyQt4.QtGui import *
from PyQt4.QtCore import *

from result_parsers import *
from models import *

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class QueryManager:
    queries = {}
    s = None

    def __init__(self, parent):
        reg = self.register_single
        reg(PerfQuery)
        reg(ExecTimeQuery)
        reg(ExecSizeQuery)

        self.parent = parent
        self.entity_manager = self.parent.entity_manager

    def register_single(self, query_class):
        self.queries[query_class.title] = query_class
        self.s = [query.title for query in self.queries.values()]
        self.s.sort()

    def get_titles(self):
        return self.s

    def get(self, title):
        QueryClass = self.queries[title]
        return QueryClass(self.entity_manager)

class Query:
    title = None
    DataModelClass = None

    def __init__(self, entity_manager):
        if self.title is None or self.DataModelClass is None:
            raise Exception("too abstract!")

        self.entity_manager = entity_manager

        self.entities = self.entity_manager.entityList
        self.query_data = {}

        self.parse()
        self.build_columns()

    def get_model(self):
        raise Exception("too abstract")

    def parse(self):
        for entity in self.entities:
            self.parse_entity(entity)

    def build_columns(self):
        for entity in self.entities:
            d = {}

            for (col_title, col_function) in self.columns:
                d[col_title] = col_function(entity)

            self.query_data[entity.source.name] = d

    def parse_entity(self, entity):
        instances = self.get_needed_instances(entity)
        self.check_instance_results_presence(instances)
        self.run_parsers(instances)

    def get_needed_instances(self, entity):
        instances = [i for i in entity.instances['clang'].values()]
        instances = [i for i in instances if i.opt in self.opts]

        return instances

    def check_instance_results_presence(self, instances):
        for i in instances:
            self.results_available_for_instance(i)

    def results_available_for_instance(self, instance):
        tag_not_present = [tag not in instance.results for tag in self.result_tags]

        if any(tag_not_present):
            print(tag_not_present)
            print(instance.results.keys())
            raise Exception("Some results are not available!")
        else:
            pass

    def run_parsers(self, instances):
        for i in instances:
            for tag in self.result_tags:
                i.results[tag].parse()

    def get_model(self):
        column_titles = [col[0] for col in self.columns]
        return self.DataModelClass(self.query_data, column_titles)

class PerfQuery(Query):
    title = "perf results"
    result_tags = ['perf']
    opts = ['-O0', '-O1', '-O2', '-O3']
    DataModelClass = ExecSizeQueryDataModel

    data_for_opt = lambda entity, opt: entity.instances['clang'][opt].results['perf'].parsed_data

    cycles_for_opt = lambda entity, opt: PerfQuery.data_for_opt(entity, opt)['cycles']
    insns_for_opt = lambda entity, opt: PerfQuery.data_for_opt(entity, opt)['instructions']

    ipc_for_opt = lambda entity, opt: \
                  float(PerfQuery.cycles_for_opt(entity, opt)) / \
                  PerfQuery.insns_for_opt(entity, opt)

    columns = [
        # ('-O0 cycles', lambda entity: PerfQuery.cycles_for_opt(entity, '-O0')),
        # ('-O1 cycles', lambda entity: PerfQuery.cycles_for_opt(entity, '-O1')),
        # ('-O2 cycles', lambda entity: PerfQuery.cycles_for_opt(entity, '-O2')),
        # ('-O3 cycles', lambda entity: PerfQuery.cycles_for_opt(entity, '-O3')),

        # ('-O0 instructions', lambda entity: PerfQuery.insns_for_opt(entity, '-O0')),
        # ('-O1 instructions', lambda entity: PerfQuery.insns_for_opt(entity, '-O1')),
        # ('-O2 instructions', lambda entity: PerfQuery.insns_for_opt(entity, '-O2')),
        # ('-O3 instructions', lambda entity: PerfQuery.insns_for_opt(entity, '-O3')),

        ('-O0 IPC', lambda entity: PerfQuery.ipc_for_opt(entity, '-O0')),
        ('-O1 IPC', lambda entity: PerfQuery.ipc_for_opt(entity, '-O1')),
        ('-O2 IPC', lambda entity: PerfQuery.ipc_for_opt(entity, '-O2')),
        ('-O3 IPC', lambda entity: PerfQuery.ipc_for_opt(entity, '-O3')),
    ]

    # def get_plots(self):
    #     l = []

    #     fig = Figure()
    #     canvas = FigureCanvas(fig)
    #     axes = fig.add_subplot(111)

    #     x_values = range(len(self.columns))
    #     x_labels = [col_title for (col_title, function) in self.columns]

    #     for entity_title in self.query_data:
    #         d = []

    #         for (col_title, function) in self.columns:
    #             d.append(self.query_data[entity_title][col_title])

    #         d = np.array(d)

    #         axes.plot(x_values, d, 'b')

    #     x_axis = axes.get_xaxis()
    #     x_axis.set_ticks(x_values)
    #     x_axis.set_ticklabels(x_labels)

    #     l.append(canvas)

        # return l

class ExecSizeQuery(Query):
    title = "size"
    opts = ['-O0', '-O1', '-O2', '-O3']
    result_tags = ['executable_size']
    DataModelClass = ExecSizeQueryDataModel

    dec_for_opt = lambda entity, opt: entity.instances['clang'][opt].results['executable_size'].parsed_data['dec']

    columns = [
        ('-O0 dec', lambda entity: ExecSizeQuery.dec_for_opt(entity, '-O0')),
        ('-O1 dec', lambda entity: ExecSizeQuery.dec_for_opt(entity, '-O1')),
        ('-O2 dec', lambda entity: ExecSizeQuery.dec_for_opt(entity, '-O2')),
        ('-O3 dec', lambda entity: ExecSizeQuery.dec_for_opt(entity, '-O3')),
    ]


class ExecTimeQuery(Query):
    title = "time"
    opts = ['-O0', '-O1', '-O2', '-O3']
    result_tags = ['execution_time']
    DataModelClass = ExecTimeQueryDataModel

    data_for_opt = lambda entity, opt: entity.instances['clang'][opt].results['execution_time'].parsed_data

    user_time = lambda entity, opt: ExecTimeQuery.data_for_opt(entity, opt)['user']
    system_time = lambda entity, opt: ExecTimeQuery.data_for_opt(entity, opt)['system']
    elapsed_time = lambda entity, opt: ExecTimeQuery.data_for_opt(entity, opt)['elapsed']

    columns = [
        ('-O0 dec', lambda entity: ExecTimeQuery.user_time(entity, '-O0')),
        ('-O1 dec', lambda entity: ExecTimeQuery.user_time(entity, '-O1')),
        ('-O2 dec', lambda entity: ExecTimeQuery.user_time(entity, '-O2')),
        ('-O3 dec', lambda entity: ExecTimeQuery.user_time(entity, '-O3')),
    ]

