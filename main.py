#!/usr/bin/python3
"""This is entry point of GUI application"""

from multiprocessing import Pool
from time import sleep
from application import Application, GUIApplication
from entity import *
from jobs import *
from settings import *
from functools import partial as p
from os import sys

def main():
    a = GUIApplication()
    a.run()


class Query:
    title = "some dummy query"
    opts = ['-O0', '-O3']
    result_tags = ['executable_size', 'perf']
    values = {
        'perf': ['instructions', 'cycles'],
    }

    meta = {
        'perf': [
            ('ipc', 'instructions', 'cycles', lambda a, b: a/b),
        ]
    }

    show = ['ipc', 'instructions', 'cycles']

    def __init__(self, entity_manager):
        self.entity_manager = entity_manager
        self.cols = []
        self.entity_list = [self.entity_manager.entityList[2]]

        self.run_parser()
        self.create_categories()
        self.print_log()

    def print_log(self):
        f = lambda c: any([key for key in self.show if key in c[0]])

        filtered_cols = filter(f, self.cols)
        for entity in self.entity_list:
            for c in filtered_cols:
                print( (entity.source.name, c[0], c[1](entity) ) )

        print("--------")

    def create_categories(self):
        for tag in self.values.keys():
            for value in self.values[tag]:
                self.create_category(tag, value, norm=True)

        for tag in self.meta.keys():
            for args in self.meta[tag]:
                self.create_category(tag, args, norm=True)

    def run_parser(self):
        for entity in self.entity_list:
            for instance in entity.all_instances():
                if instance.compiler.name == 'clang' and instance.opt in self.opts:
                    for tag in self.values.keys():
                        instance.results[tag].parse()


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

            self.cols.append(("{:20} {:>20} {:4}".format(tag, value, opt), f))

        if norm:
            norm_coef_f = p(norm_coef_f, functions=functions)
            for opt in self.opts:
                f = self.create_f(*params, opt=opt)
                f_n = p(norm_f, f=f, norm_coef_f=norm_coef_f)

                self.cols.append(("{:20} {:>15} norm {:4}".format(tag, value, opt), f_n))



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

def scratch():
    options = CompilerOptions()
    manager = EntityManager(options)

    explorer = FileExplorer(SINGLE_SOURCE_TESTS_ROOT)
    (source_list, include_dirs)  = explorer.find()

    manager.createEntityList(source_list)

    q = Query(manager)

if __name__ == "__main__":
    if '-s' in sys.argv:
        scratch()
    else:
        main()
