#!/usr/bin/python3
"""This is entry point of GUI application"""
from entity import *
from jobs import *
from settings import *
from os import sys
from application import GUIApplication
from printers import PerfEstCSVPrinter

from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter

def main():
    a = GUIApplication()
    a.run()

def scratch():
    manager = EntityManager()
    executor = Executor(manager)

    entity = manager.get_entity("chomp")
    instance = entity.instances['clang']['-O1']

    instance.results['cross_asm'].parse()
    parsed_asm = instance.results['cross_asm'].parsed_output['asm_fbb_tree']

    f = list(parsed_asm.keys())[0]
    bb = list(parsed_asm[f].keys())[0]

    bb_content = "\n".join(parsed_asm[f][bb])

    Lexer = get_lexer_by_name('asm')
    s = highlight(bb_content, Lexer, HtmlFormatter())
    print(s)

if __name__ == "__main__":
    if '-s' in sys.argv:
        scratch()
    else:
        main()
