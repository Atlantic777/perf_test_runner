from PyQt4.QtGui import *
from PyQt4.QtCore import *

from result_parsers import *
from models import *


class QueryManager:
    queries = {}
    s = None

    def __init__(self, parent):
        reg = self.register_single
        reg(PerfQuery)
        reg(ExecTimeQuery)
        reg(ExecSizeQuery)
        # reg(PerfTimeSizeQuery)
        reg(ExecTimeNormQuery)

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
                try:
                    d[col_title] = col_function(entity)
                except:
                    d[col_title] = 0

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

    def __init__(self, entity_manager):
        instance = lambda entity, opt: entity.instances['clang'][opt]
        result = lambda instance: instance.results['perf']

        cycles = lambda result: result.parsed_data['cycles']
        insns = lambda result: result.parsed_data['instructions']
        ipc = lambda result: float(cycles(result)) / insns(result)

        f_opt = lambda entity, opt: ipc(result(instance(entity, opt)))

        f_0 = lambda entity: f_opt(entity, '-O0')
        f_1 = lambda entity: f_opt(entity, '-O1')
        f_2 = lambda entity: f_opt(entity, '-O2')
        f_3 = lambda entity: f_opt(entity, '-O3')

        self.columns = [
            ('-O0 IPC', f_0),
            ('-O1 IPC', f_1),
            ('-O2 IPC', f_2),
            ('-O3 IPC', f_3),
        ]

        super().__init__(entity_manager)

class ExecSizeQuery(Query):
    title = "size"
    opts = ['-O0', '-O1', '-O2', '-O3']
    result_tags = ['executable_size']
    DataModelClass = ExecSizeQueryDataModel

    def __init__(self, entity_manager):
        instance = lambda entity, opt: entity.instances['clang'][opt]
        result = lambda instance: instance.results['executable_size']
        dec = lambda result: result.parsed_data['dec']

        f_opt = lambda entity, opt: dec(result(instance(entity, opt)))

        f_0 = lambda entity: f_opt(entity, '-O0')
        f_1 = lambda entity: f_opt(entity, '-O1')
        f_2 = lambda entity: f_opt(entity, '-O2')
        f_3 = lambda entity: f_opt(entity, '-O3')

        self.columns = [
            ('-O0 dec', f_0),
            ('-O1 dec', f_1),
            ('-O2 dec', f_2),
            ('-O3 dec', f_3),
        ]

        super().__init__(entity_manager)


class ExecTimeQuery(Query):
    title = "time"
    opts = ['-O0', '-O1', '-O2', '-O3']
    result_tags = ['execution_time']
    DataModelClass = ExecTimeQueryDataModel

    def __init__(self, entity_manager):
        instance = lambda entity, opt: entity.instances['clang'][opt]
        result = lambda instance: instance.results['execution_time']
        elapsed = lambda result: result.parsed_data['user']

        f_opt = lambda entity, opt: elapsed(result(instance(entity, opt)))

        f_0 = lambda entity: f_opt(entity, '-O0')
        f_1 = lambda entity: f_opt(entity, '-O1')
        f_2 = lambda entity: f_opt(entity, '-O2')
        f_3 = lambda entity: f_opt(entity, '-O3')

        self.columns = [
            ('-O0 u_sec', f_0),
            ('-O1 u_sec', f_1),
            ('-O2 u_sec', f_2),
            ('-O3 u_sec', f_3),
        ]

        super().__init__(entity_manager)

class PerfTimeSizeQuery(Query):
    title = 'perf time size'
    opts = ['-O0', '-O1', '-O2', '-O3']
    result_tags = ['perf', 'execution_time', 'execution_size']
    DataModelClass = PerfTimeSizeDataModel

    def __init__(self, entity_manager):
        self.columns = []
        super().__init__(entity_manager)

class ExecTimeNormQuery(Query):
    title = "time (norm)"
    opts = ['-O0', '-O1', '-O2', '-O3']
    result_tags = ['execution_time']
    DataModelClass = ExecTimeQueryDataModel

    def __init__(self, entity_manager):
        instance = lambda entity, opt: entity.instances['clang'][opt]
        result = lambda instance: instance.results['execution_time']
        elapsed = lambda result: result.parsed_data['user']

        f_opt = lambda entity, opt: elapsed(result(instance(entity, opt)))

        f_0p = lambda entity: f_opt(entity, '-O0')
        f_1p = lambda entity: f_opt(entity, '-O1')
        f_2p = lambda entity: f_opt(entity, '-O2')
        f_3p = lambda entity: f_opt(entity, '-O3')

        norm_coef = lambda e: max([f_0p(e), f_1p(e), f_2p(e), f_3p(e)])

        f_0 = lambda entity: float(f_0p(entity)) / norm_coef(entity)
        f_1 = lambda entity: float(f_1p(entity)) / norm_coef(entity)
        f_2 = lambda entity: float(f_2p(entity)) / norm_coef(entity)
        f_3 = lambda entity: float(f_3p(entity)) / norm_coef(entity)

        self.columns = [
            ('-O0 u_sec', f_0),
            ('-O1 u_sec', f_1),
            ('-O2 u_sec', f_2),
            ('-O3 u_sec', f_3),
        ]

        super().__init__(entity_manager)
