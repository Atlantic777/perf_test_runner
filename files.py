"""
Abstract class with instances to encapsulate representation
of various files on disk
"""

class File:
    """
    This is the base class for representing files on disk
    """
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
    """ Just an alias for the File class """
    pass

class SourceFile(File):
    """ Just an alias for the File class """
    pass
