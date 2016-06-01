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
        reg(PerfEstQuery)

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
    opts = ['-O0', '-O1', '-O2', '-O3']

    values = {}
    meta = {}
    show = []
    plot = ['norm']


    def __init__(self, entity_manager):
        if self.title is None:
            raise Exception("too abstract!")

        self.columns = []
        self.entity_manager = entity_manager

        self.entities = self.entity_manager.entityList
        self.query_data = {}

        self.parse()
        self.build_lambdas()
        self.build_columns()

    def build_lambdas(self):
        for tag in self.values.keys():
            for value in self.values[tag]:
                self.create_category(tag, value, norm=True)

        for tag in self.meta.keys():
            for args in self.meta[tag]:
                self.create_category(tag, args, norm=True)

    def create_category(self, tag, args, norm=False):
        value = None
        params = None

        if type(args) == type( str() ):
            value = args
            params = [tag, args]
        else:
            value = args[0]
            params = [tag] + list(args)

        functions = []

        norm_coef_f = lambda entity, functions: max([f(entity) for f in functions])
        norm_f = lambda entity, f, norm_coef_f: f(entity)/norm_coef_f(entity)

        for opt in self.opts:
            f = self.create_f(*params, opt=opt)
            functions.append(f)

            self.columns.append(("{} {}".format(value, opt), f))

        if norm:
            norm_coef_f = p(norm_coef_f, functions=functions)
            for opt in self.opts:
                f = self.create_f(*params, opt=opt)
                f_n = p(norm_f, f=f, norm_coef_f=norm_coef_f)

                self.columns.append(("{} norm {}".format(value, opt), f_n))

    def create_f(self, *args, **kwargs):
        is_meta = False

        (tag, value, title, value_1, value_2, op) = [None for i in range(6)]
        opt = kwargs['opt']

        if len(args) == 2:
            (tag, value) = args
        elif len(args) == 5:
            is_meta = True
            (tag, title, value_1, value_2, op) = args


        results_obj = lambda entity, opt: entity.instances['clang'][opt].results
        tag_f = lambda entity, tag, r: r(entity)[tag].parsed_data
        mother_f = lambda entity, value, tag: tag(entity)[value]

        r = p(results_obj, opt=opt)
        e = p(tag_f, tag=tag, r=r)

        f = None
        if is_meta:
            meta_f = lambda entity, value_1, value_2: op(value_1(entity), value_2(entity))
            f1 = p(mother_f, tag=e, value=value_1)
            f2 = p(mother_f, tag=e, value=value_2)
            f = p(meta_f, value_1=f1, value_2=f2) 
        else:
            f = p(mother_f, tag=e, value=value)

        return f

    def get_model(self):
        raise Exception("too abstract")

    def parse(self):
        for entity in self.entities:
            try:
                self.parse_entity(entity)
            except Exception as e:
                print("Can't parse: " + str(entity))
                print(e)

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

    def get_visible_columns(self):
        if self.show == []:
            return self.columns

        f = lambda c: any([key for key in self.show if key in c[0]])
        filtered_cols = [col for col in self.columns if f(col)]

        return filtered_cols

    def get_plotable_cols(self):
        if self.plot == []:
            return self.columns

        f = lambda c: any([key for key in self.plot if key in c[0]])
        filtered_cols = [col for col in self.columns if f(col)]

        return filtered_cols

class PerfQuery(Query, QueryDataTableModel):
    title = "perf results"
    values = {
        'perf' : ['cycles', 'instructions'],
    }

    meta = {
        'perf' : [
            ('ipc', 'instructions', 'cycles', lambda a, b: a / b),
        ]
    }

    show = [
        'ipc norm',
    ]

    plot = [
        'ipc norm',
    ]

    def __init__(self, entity_manager):
        Query.__init__(self, entity_manager)
        QueryDataTableModel.__init__(self)

    def get_model(self):
        return self

class ExecSizeQuery(Query, QueryDataTableModel):
    title = "size"
    values = {
        'executable_size': ['dec'],
    }

    meta = {}
    show = ['dec']

    def __init__(self, entity_manager):
        Query.__init__(self, entity_manager)
        QueryDataTableModel.__init__(self)

    def get_model(self):
        return self

class ExecTimeQuery(Query, QueryDataTableModel):
    title = "time"
    values = {
        'execution_time' : ['user'],
    }

    def __init__(self, entity_manager):
        Query.__init__(self, entity_manager)
        QueryDataTableModel.__init__(self)

    def get_model(self):
        return self

class PerfTimeSizeQuery(Query, QueryDataTableModel):
    title = 'perf time size'
    values = {
        'executable_size' : ['dec'],
        'perf' : ['instructions', 'branches', 'cycles', 'page-faults'],
        'execution_time' : ['elapsed'],
    }

    plot = ['instructions norm']

    def __init__(self, entity_manager):
        Query.__init__(self, entity_manager)
        QueryDataTableModel.__init__(self)

    def get_model(self):
        return self

class PerfEstQuery(Query, QueryDataTableModel):
    title = 'perf est query'
    values = {
        'perf_est_fron': ['estimation']
    }

    pot = ['estimation norm']

    def __init__(self, entity_manager):
        Query.__init__(self, entity_manager)
        QueryDataTableModel.__init__(self)

    def get_model(self):
        return self
