#!/usr/bin/python3
from entity import EntityManager
from jobs import Executor, CrossCompileJob, CrossAsmJob, TimeCrossJob
from settings import Scope

def main():
    manager = EntityManager(preload=True)
    executor = Executor(manager)

    scope = Scope()
    scope.domain = "entity"
    scope.entity = 'huffbench'

    # executor.execute(CrossAsmJob, scope, force=False, verbose=True)
    # executor.execute(CrossCompileJob, scope, force=True, verbose=True)
    executor.execute(TimeCrossJob, scope, force=True, verbose=True)

    # e = manager.get_entity(scope.entity)
    # for i in e.all_instances():
    #     print(i)
    #     print('cross_asm: ', 'cross_asm' in i.results.keys())
    #     print('cross_comp: ', 'cross_comp' in i.results.keys())

if __name__ == "__main__":
    main()
