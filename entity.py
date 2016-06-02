"""
Test source files, their instances and their manager:
"""
from os import path
from settings import OUTPUT_ROOT
from results import *
from jobs import *

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

    def all_instances(self):
        for comp_dict in self.instances.values():
            for instance in comp_dict.values():
                yield instance

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

    def __init__(self, buildOptions=None, preload=True):
        if buildOptions:
            self.buildOptions = buildOptions
        else:
            self.buildOptions = CompilerOptions()

        self.explorer = FileExplorer(SINGLE_SOURCE_TESTS_ROOT)
        (self.source_list, self.include_dirs) = self.explorer.find()

        self.createEntityList(self.source_list, preload)


    def createEntityList(self, sourceList, preload=True):
        """
        Given the list of test sources create list of entities
        """
        self.entityList = []

        for source in sourceList:
            self.entityList.append(Entity(source, self.buildOptions))

        if preload:
            self.discover_result_files()

    def discover_result_files(self):
        for instance in self.all_instances():
            self._load_existing_results(instance)

    def all_instances(self):
        for entity in self.entityList:
            for opt in entity.instances.values():
                for instance in opt.values():
                    yield instance

    def all_entities(self):
        for entity in self.entityList:
            yield entity

    def _load_existing_results(self, instance):
        results = [
            CompilationResult,
            GenerateBitcodeResult,
            OptimiserStatsResult,
            PerfResult,
            ExecutableSizeResult,
            TimeExecutionResult,
            CrossAsmResult,
            CrossCompileResult,
            PerfEstResult,
            TimeCrossResult,
        ]

        for Res in results:
            r = Res(instance)
            r.load()

    def get_entity(self, entity_name):
        for entity in self.entityList:
            if entity_name in entity.source.name:
                return entity

    # def getInstances(self, scopes):
    #     entities = self._getEntities(scopes)
    #     instances = self._filterInstances(entities, scopes)

    #     return instances

    # def _getEntities(self, scopes):
    #     s = scopes['entity']

    #     parent = self.parent()
    #     entity_manager = parent.entity_manager

    #     entities = None

    #     if s == 0:
    #         entities = entity_manager.all_instances()
    #     elif (s == 1 or s == 2) and parent.selected_entity is not None:
    #         entities = parent.selected_entity.all_instances()
    #     else:
    #         entities = []

    #     return entities

    # def _filterInstances(self, instances, scopes):
    #     final_instances_list = []

    #     parent = self.parent()
    #     selected_entity = parent.selected_entity
    #     selected_instance = parent.selected_instance

    #     if scopes['entity'] == 2 and selected_instance is not None:
    #         return  [ selected_instance ]

    #     for instance in instances:
    #         if self._checkSingleInstance(instance, scopes):
    #             final_instances_list.append(instance)

    #     return final_instances_list

    # def _checkSingleInstance(self, instance, scopes):
    #     selected_compilers = scopes['compiler']
    #     selected_optims = scopes['optimisation']

    #     compiler_ok = instance.compiler.name in selected_compilers
    #     optim_ok = instance.opt in selected_optims

    #     if compiler_ok and optim_ok:
    #         return True
    #     else:
    #         return False

