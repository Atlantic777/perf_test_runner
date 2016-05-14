"""
Test source files, their instances and their manager:
"""
from os import path

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

class EntityManager:
    """
    Collect all entities together

    can discover source files
    TODO: discover result files
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

    def discover_result_files(self):
        raise Exception("Not yet implemented!")

        for entity in self.entityList:
            # guess result file path
            # try to open it
            # add to entity structure
            pass
