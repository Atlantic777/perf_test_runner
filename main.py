#!/usr/bin/python3
"""This is entry point of GUI application"""
from entity import *
from jobs import *
from settings import *
from os import sys
from application import GUIApplication

def main():
    a = GUIApplication()
    a.run()

def scratch():
    manager = EntityManager()
    executor = Executor(manager)

    entity = manager.get_entity("chomp")
    instance = entity.instances['clang']['-O1']

    x_asm_res = instance.results['cross_asm']

    f_path = x_asm_res.action_output_file.full_path

    print(instance)
    print(f_path)

    asm_fbb_tree = {}
    current_func = None
    current_bb = None
    current_l = None

    with open(f_path, "r") as f:
        for l in f:
            if "# @" in l and l[0] != '\t':
                func_name = l.split(':')[0]
                asm_fbb_tree[func_name] = {}
                current_func = func_name

                print("\n"*2+"="*60)
                print(func_name)
                print("="*60)
            elif "# %" in l:
                bb_name = l.split('# %')[1][:-1]
                l = []
                asm_fbb_tree[current_func][bb_name] = l
                current_bb = bb_name
                current_l = l

                print(bb_name)
                print("-"*60)
            elif current_func and current_bb:
                current_l.append(l[:-1])
                print(l[:-1])
            else:
                print(l[:-1])

    while True:
        f = input("function name: ")
        bb = input("bb name: ")

        for l in asm_fbb_tree[f][bb]:
            print(l)

if __name__ == "__main__":
    if '-s' in sys.argv:
        scratch()
    else:
        main()
