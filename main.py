#!/usr/bin/python3
"""This is entry point of GUI application"""

from multiprocessing import Pool
from time import sleep
from application import Application, GUIApplication
from entity import *
from jobs import *
from settings import *

def main():
    a = GUIApplication()
    a.run()

def scratch():
    options = CompilerOptions()
    manager = EntityManager(options)

    explorer = FileExplorer(SINGLE_SOURCE_TESTS_ROOT)
    (source_list, include_dirs)  = explorer.find()

    manager.createEntityList(source_list)

    instance = manager.entityList[0].instances['clang']['-O3']
    res = instance.results['execution_time']
    res.parse()

    for tag in res.parsed_data:
        print("{:<10} : {:>20}".format(tag, res.parsed_data[tag]))

if __name__ == "__main__":
    main()
    # scratch()
