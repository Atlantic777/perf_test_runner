#!/usr/bin/python3
from entity import EntityManager
from jobs import Executor, TimeExecutionJob, CompilerJob
from settings import Scope

def main():
    manager = EntityManager(preload=True)
    executor = Executor(manager)

    scope = Scope()

    executor.execute(TimeExecutionJob, scope, force=True)

if __name__ == "__main__":
    main()
