from entity import EntityManager
from PyQt4.QtCore import (
    QAbstractListModel,
    QAbstractTableModel,
    QVariant,
)

from PyQt4 import QtCore

class EntityManagerListModel(QAbstractListModel):
    def __init__(self, manager):
        super(EntityManagerListModel, self).__init__()
        self.manager = manager

    def rowCount(self, parent=None):
        count =  len(self.manager.entityList)
        return count

    def data(self, index, role):
        if not index.isValid():
            return None
        if role == QtCore.Qt.DisplayRole:
            return str(self.manager.entityList[index.row()])
        else:
            return None

class EntityTableModel(QAbstractTableModel):
    def __init__(self, entity=None):
        super().__init__()
        self.entity = entity

    def rebuild_internal_structures(self):
        self.compilers = list( self.entity.instances.keys() )
        self.optims = list(self.entity.instances[self.compilers[0]].keys())

    def __str__(self):
        return self.entity.source.name + " " + self.entity.source.path

    def columnCount(self, index):
        if self.entity is None:
            return 0
        else:
            cols =  max([len(opts) for opts in self.entity.instances.values()])
            return cols # the one for compiler name

    def rowCount(self, index):
        if self.entity is None:
            return 0
        else:
            return len(self.entity.instances) # compilers count

    def data(self, index, role):
        if self.entity is None:
            return None

        if role == QtCore.Qt.DisplayRole:
            instance = self.getInstanceAt(index.row(), index.column())
            return instance.getHash()
        else:
            return None

    def headerData(self, section, orientation, role):
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return self.optims[section]
            elif orientation == QtCore.Qt.Vertical:
                return self.compilers[section]

    def setEntity(self, entity):
        self.beginResetModel()

        self.entity = entity
        self.rebuild_internal_structures()

        self.endResetModel()

    def getInstanceAt(self, row, col):
        compiler = self.compilers[row]
        opt = self.optims[col]

        return self.entity.instances[compiler][opt]
