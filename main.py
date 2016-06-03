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

def describe(instance):
    r_fron = instance.results['perf_est_fron']
    r_back = instance.results['perf_est_back']

    r_fron.parse()
    r_back.parse()

    fron_freq_d = r_fron.parsed_data['freq']
    back_freq_d = r_back.parsed_data['freq']

    for function in fron_freq_d.keys():
        for block in fron_freq_d[function].keys():
            if function not in back_freq_d or block not in back_freq_d[function]:
                continue

            d1 = fron_freq_d[function][block]
            d2 = back_freq_d[function][block]

            n1 = float(d1['norm_freq'])
            n2 = float(d2['norm_freq'])

            cnt1 = float(d1['cnt'])
            cnt2 = float(d2['cnt'])

            fmt = "{:100} {:20.2f} {:20.2f} {:20.2f} {:20.2f}"
            s = fmt.format(
                ' '.join([instance.parent.source.name, instance.opt, function, block]),
                n1,
                n2,
                cnt1,
                cnt2,
            )

            print(s)

def scratch():
    manager = EntityManager()
    executor = Executor(manager)

    scope = Scope()
    scope.domain = "everything"

    executor.execute(PerfEstJob, scope, force=False, verbose=True)
    executor.execute(PerfEstBackJob, scope, force=False, verbose=True)

    for entity in manager.entityList:
        for instance in entity.all_instances():
            if instance.opt in scope.opts and instance.compiler.name in scope.compilers:
                describe(instance)

if __name__ == "__main__":
    if '-s' in sys.argv:
        scratch()
    else:
        main()
