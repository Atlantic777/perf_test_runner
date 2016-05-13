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
    columns = [
        'compiler',
        'opt',
    ]

    def __init__(self, entity=None):
        super().__init__()
        self.entity = entity

    def build_instances(self):
        if self.entity is None:
            self.instances = None
            return

        self.instances = []

        for comp in list(self.entity.instances):
            for opt in list(self.entity.instances[comp]):
                self.instances.append(self.entity.instances[comp][opt])

    def __str__(self):
        return self.entity.source.name + " " + self.entity.source.path

    def columnCount(self, index):
        return len(self.columns)

    def rowCount(self, index):
        if self.entity is None:
            return 0
        else:
            return len(self.instances)

    def data(self, index, role):
        if self.entity is None:
            return None

        if role == QtCore.Qt.DisplayRole:
            if index.column() == 0:
                return self.instances[index.row()].compiler.name
            elif index.column() == 1:
                return self.instances[index.row()].opt
        else:
            return None

    def setEntity(self, entity):
        self.beginResetModel()

        self.entity = entity
        self.build_instances()

        print(len( self.instances ))


        self.endResetModel()
