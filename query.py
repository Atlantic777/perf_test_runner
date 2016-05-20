from PyQt4.QtGui import *
from PyQt4.QtCore import *

from result_parsers import *
from models import PerfQueryDataModel

class QueryManager:
    queries = {}
    s = None

    def __init__(self, parent):
        reg = self.register_single
        reg(PerfQuery)
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

    def __init__(self, entity_manager):
        if self.title is None:
            raise Exception("too abstract!")

        self.entity_manager = entity_manager

    def get_model(self):
        raise Exception("too abstract")

class PerfQuery(Query):
    title = "perf results"

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

    result_tags = ['perf']

    def __init__(self, manager):
        super().__init__(manager)

        self.entities = []
        self.parsed_perf_results = {}

        self.fetch_dataset()
        self.parse()
        self.build_columns()

    # -----------  first level methods ----------------------
    def fetch_dataset(self):
        self.entities = self.entity_manager.entityList

    def parse(self):
        for entity in self.entities:
            self.parse_entity(entity)

    def build_columns(self):
        self.query_data = {}

        for entity in self.entities:
            d = {}

            for (col_title, col_function) in self.columns:
                d[col_title] = col_function(entity)

            self.query_data[entity.source.name] = d
    # ----------- end of first level methods -----------------

    # ---------- parsing phase -------------------
    def parse_entity(self, entity):
        instances = self.get_needed_instances(entity)
        self.check_instance_results_presence(instances)
        self.run_parsers(instances)

    def get_needed_instances(self, entity):
        opts = ['-O0', '-O1', '-O2', '-O3']

        instances = [i for i in entity.instances['clang'].values()]
        instances = [i for i in instances if i.opt in opts]

        return instances

    def check_instance_results_presence(self, instances):
        for i in instances:
            self.results_available_for_instance(i)

    def results_available_for_instance(self, instance):
        tag_not_present = [tag not in instance.results for tag in self.result_tags]

        if any(tag_not_present):
            raise Exception("Some results are not available!")
        else:
            pass

    def run_parsers(self, instances):
        for i in instances:
            for tag in self.result_tags:
                i.results[tag].parse()
    # ------ end of parsing phase methods ------------------

    def get_model(self):
        column_titles = [col[0] for col in self.columns]
        return PerfQueryDataModel(self.query_data, column_titles)

class ExecSizeQuery(Query):
    title = "size"

    def get_model(self):
        return None
