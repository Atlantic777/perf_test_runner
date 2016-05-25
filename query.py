from PyQt4.QtGui import *
from PyQt4.QtCore import *

from result_parsers import *
from models import *
from functools import partial as p

class QueryManager:
    queries = {}
    s = None

    def __init__(self, parent):
        reg = self.register_single
        reg(PerfQuery)
        reg(ExecTimeQuery)
        reg(ExecSizeQuery)
        reg(PerfTimeSizeQuery)
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
    values = {}
    columns = []
    opts = ['-O0', '-O1', '-O2', '-O3']

    def __init__(self, entity_manager):
        if self.title is None or self.DataModelClass is None:
            raise Exception("too abstract!")

        self.entity_manager = entity_manager

        self.entities = self.entity_manager.entityList
        self.query_data = {}

        self.parse()
        self.build_lambdas()
        self.build_columns()

    def build_lambdas(self):
        for tag in self.values.keys():
            for value in self.values[tag]:
                self.create_category(tag, value)

    def create_category(self, tag, value):
        results_obj = lambda entity, opt: entity.instances['clang'][opt].results
        tag_f = lambda entity, tag, r: r(entity)[tag].parsed_data
        mother_f = lambda entity, value, tag: tag(entity)[value]

        for opt in self.opts:
            r = p(results_obj, opt=opt)
            e = p(tag_f, tag=tag, r=r)
            f = p(mother_f, tag=e, value=value)

            self.columns.append(("{} {}".format(value, opt), f))

    def get_model(self):
        raise Exception("too abstract")

    def parse(self):
        for entity in self.entities:
            try:
                self.parse_entity(entity)
            except Exception as e:
                print("Can't parse: " + str(entity))

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
        tag_not_present = [tag not in instance.results for tag in self.values.keys()]

        if any(tag_not_present):
            print(tag_not_present)
            print(instance.results.keys())
            raise Exception("Some results are not available!")
        else:
            pass

    def run_parsers(self, instances):
        for i in instances:
            for tag in self.values.keys():
                i.results[tag].parse()

    def get_model(self):
        column_titles = [col[0] for col in self.columns]
        return self.DataModelClass(self.query_data, column_titles)

class PerfQuery(Query):
    title = "perf results"
    DataModelClass = ExecSizeQueryDataModel
    values = {
        'perf' : ['cycles', 'instructions'],
    }

class ExecSizeQuery(Query):
    title = "size"
    DataModelClass = ExecSizeQueryDataModel
    values = {
        'executable_size': ['dec'],
    }

class ExecTimeQuery(Query):
    title = "time"
    DataModelClass = ExecTimeQueryDataModel
    values = {
        'execution_time' : ['user'],
    }

class PerfTimeSizeQuery(Query):
    title = 'perf time size'
    DataModelClass = PerfTimeSizeDataModel
    values = {
        'executable_size' : ['dec'],
        'perf' : ['instructions', 'branches', 'cycles', 'page-faults'],
        'execution_time' : ['elapsed'],
    }

class ExecTimeNormQuery(Query):
    title = "time (norm)"
    DataModelClass = ExecTimeQueryDataModel
    values = {
        'execution_time' : ['elapsed']
    }
