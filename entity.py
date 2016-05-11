from os import path

class Entity:
    def __init__(self, source, options):
        entities = {}

        for compiler in options.compilers_list:
            entities[compiler.name] = {}

            for opt in options.optim_levels_list:
                e = EntityInstance(compiler, opt)
                entities[compiler.name][opt] = e

        self.source = source

    def __str__(self):
        return self.source.name

class EntityInstance:
    def __init__(self, compiler, opt):
        pass

class EntityManager:
    entityList = []
    buildOptions = None

    def __init__(self, buildOptions):
        self.buildOptions = buildOptions

    def createEntityList(self, sourceList):
        self.entityList = []

        for source in sourceList:
            self.entityList.append(Entity(source, self.buildOptions))
