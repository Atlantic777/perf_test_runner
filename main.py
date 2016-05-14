#!/usr/bin/python3
"""This is entry point of GUI application"""

from multiprocessing import Pool
from time import sleep
from application import Application, GUIApplication
from entity import *
from jobs import *

def main():
    a = GUIApplication()
    a.run()

def scratch():
    options = CompilerOptions()

    explorer = FileExplorer()
    (sources_list, include_list) = explorer.find()

    manager = EntityManager(options)
    manager.createEntityList(sources_list)

    for e in manager.entityList:
        print(e)


if __name__ == "__main__":
    main()
    # scratch()
