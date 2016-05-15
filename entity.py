"""
Test source files, their instances and their manager:
"""
from os import path
from settings import OUTPUT_ROOT
from results import *

class Entity:
    """
    A test source with it's instances

    For every compiler and optimization level there is an EntityInstance
    in the self.instances.

    The SourceFile representing the file on disk is in self.source
    """
    def __init__(self, source, options):
        self.instances = {}

        for compiler in options.compilers_list:
            self.instances[compiler.name] = {}

            for opt in options.optim_levels_list:
                e = EntityInstance(self, compiler, opt)
                self.instances[compiler.name][opt] = e

        self.source = source

    def __str__(self):
        return self.source.name

class EntityInstance:
    """
    Represents tuple (compiler, optimisation level) with
    various result data attached in self.results ditc.
    """
    def __init__(self, parent, compiler, opt):
        self.parent = parent
        self.compiler = compiler
        self.opt = opt
        self.results = {}
        self._hash = None

    def getHash(self):
        if self._hash is None:
            return "<hash>"
        else:
            return self._hash

    def __repr__(self):
        return str( (self.parent.source.name, self.compiler.name, self.opt) )

    def getOutputPath(self):
        compiler = self.compiler.name
        optim = self.opt

        d = path.join(OUTPUT_ROOT, compiler, optim.strip('-').lower())
        return d

class EntityManager:
    """
    Collect all entities together

    - can discover source files
    - can discover result files
    """
    entityList = []
    buildOptions = None

    def __init__(self, buildOptions):
        self.buildOptions = buildOptions

    def createEntityList(self, sourceList):
        """
        Given the list of test sources create list of entities
        """
        self.entityList = []

        for source in sourceList:
            self.entityList.append(Entity(source, self.buildOptions))

        self.discover_result_files()

    def discover_result_files(self):
        for instance in self.all_instances():
            self._load_existing_results(instance)

    def all_instances(self):
        for entity in self.entityList:
            for opt in entity.instances.values():
                for instance in opt.values():
                    yield instance

    def _load_existing_results(self, instance):
        results = [
            CompilationResult,
            GenerateBitcodeResult,
            OptimiserStatsResult,
            PerfResult,
            ExecutableSizeResult,
            TimeExecutionResult,
        ]

        for Res in results:
            r = Res(instance)
            r.load()

