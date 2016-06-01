#!/usr/bin/python3
from entity import EntityManager
from jobs import Executor, TimeCrossJob
from settings import Scope
import pickle

def main():
    manager = None

    try:
        f = open("manager.dat", "rb")
        manager = pickle.load(f)
        print("manager is loaded!")
    except:
        print("creating a new manager")
        manager = EntityManager(preload=True)

    executor = Executor(manager)

    scope = Scope()
    scope.domain = "everything"

    executor.execute(TimeCrossJob, scope, force=False, verbose=True)

    with open("manager.dat", "wb") as f:
       pickle.dump(manager, f)
       print("saving manager to file...")


if __name__ == "__main__":
    main()
