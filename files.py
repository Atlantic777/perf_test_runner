class File:
    name = None
    path = None

    def __init__(self, path, name):
        self.path = path
        self.name = name

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

class Compiler(File):
    pass

class SourceFile(File):
    pass
