#!/usr/bin/python3
"""This is entry point of GUI application"""
from entity import *
from jobs import *
from settings import *
from os import sys
from application import GUIApplication
from printers import PerfEstCSVPrinter

def main():
    a = GUIApplication()
    a.run()

def scratch():
    manager = EntityManager()
    executor = Executor(manager)

    entity = manager.get_entity("chomp")
    instance = entity.instances['clang']['-O1']

    p = PerfEstCSVPrinter(instance.results)
    print(p.get_report())

    # x_asm_res.parse()

    # i = 1
    # for f in x_asm_res.parsed_output.keys():
    #     for bb in x_asm_res.parsed_output[f].keys():
    #         print("{:3}) {:30} - {:30}".format(i, f, bb))
    #         i += 1

if __name__ == "__main__":
    if '-s' in sys.argv:
        scratch()
    else:
        main()
