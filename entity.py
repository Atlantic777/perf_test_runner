from os import path

class Entity:
    def __init__(self, sourcePath, options):
        entities = {}

        for compiler in options.compilers_list:
            entities[compiler] = {}

            for opt in options.optim_levels_list:
                e = EntityInstance(sourcePath, compiler, opt)
                entities[compiler.name][opt] = e

        self.name = path.basename(sourcePath)
        self.sourcePath = sourcePath

    def __str__(self):
        return self.name

class EntityInstance:
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
