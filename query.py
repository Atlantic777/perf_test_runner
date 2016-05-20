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

    columns = [
        ('-O0 cycles', 'cycles'),
        ('-O0 instructions', 'instructions'),
        ('IPC', None),
    ]

    def __init__(self, manager):
        super().__init__(manager)

        self.entities = []
        self.parsed_perf_results = {}

        self.fetch_dataset()
        self.parse()

    def fetch_dataset(self):
        self.entities = self.entity_manager.entityList.copy()

        for entity in self.entities:
            self.parse_entity(entity)

    def parse(self):
        for entity in self.entities:
            self.parse_entity(entity)

    def parse_entity(self, entity):
        instance = entity.instances['clang']['-O0']
        parsed = self.parse_instance(instance)

        extracted = {}

        for (dest, src) in self.columns:
            if src is not None:
                extracted[dest] = parsed[src]
            elif dest == 'IPC':
                extracted[dest] = float(parsed['instructions']) / parsed['cycles']

        self.parsed_perf_results[str(entity)] = extracted

    def parse_instance(self, instance):
        raw_result = instance.results['perf'].raw_output
        parsed = PerfResultParser(raw_result).values

        return parsed

    def get_model(self):
        return PerfQueryDataModel(self.parsed_perf_results)

class ExecSizeQuery(Query):
    title = "size"

    def get_model(self):
        return None
