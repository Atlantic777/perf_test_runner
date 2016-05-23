"""
Models which encapsulate raw data structures
in a way suitable for MVC and Qt widgets
"""
from entity import EntityManager
from PyQt4.QtCore import (
    QAbstractListModel,
    QAbstractTableModel,
    QVariant,
)

from PyQt4 import QtCore
from PyQt4 import QtGui

class EntityManagerListModel(QAbstractListModel):
    def __init__(self, manager):
        super(EntityManagerListModel, self).__init__()
        self.manager = manager

    def rowCount(self, parent=None):
        count =  len(self.manager.entityList)
        return count

    def data(self, index, role):
        entity = self.manager.entityList[index.row()]
        if not index.isValid():
            return None
        if role == QtCore.Qt.DisplayRole:
            return str(entity)
        if role == QtCore.Qt.BackgroundRole:
            has_any = False
            has_all = True

            for instance in entity.all_instances():
                is_clang = instance.compiler.name == 'clang'
                has_executable = 'compilation' in instance.results

                if is_clang:
                    has_any = has_any or has_executable
                    has_all = has_all and has_executable

            if has_all:
                return QtGui.QBrush(QtGui.QColor("green"))
            elif has_any:
                return QtGui.QBrush(QtGui.QColor("lightGreen"))
            else:
                return None
        else:
            return None

class EntityTableModel(QAbstractTableModel):
    def __init__(self, entity=None):
        super().__init__()
        self.entity = entity

    def rebuild_internal_structures(self):
        self.compilers = list( self.entity.instances.keys() )
        self.compilers.sort()

        self.optims = list(self.entity.instances[self.compilers[0]].keys())
        self.optims.sort()

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

        instance = self.getInstanceAt(index.row(), index.column())

        if role == QtCore.Qt.DisplayRole:
            return instance.getHash()
        if role == QtCore.Qt.BackgroundRole:
            if instance.getHash() == "<hash>":
                return QtGui.QBrush(QtGui.QColor("red"))
            else:
                return QtGui.QBrush(QtGui.QColor("lightGreen"))
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

class PerfQueryDataModel(QAbstractTableModel):
    def __init__(self, parsed_perf_results, column_titles):
        super().__init__()
        self.values = parsed_perf_results

        self.entity_titles = list(self.values.keys())
        self.entity_titles.sort()

        self.columns = column_titles

    def columnCount(self, index):
        return len(self.columns) + 1

    def rowCount(self, index):
        return len(self.entity_titles)

    def data(self, index, role):
        row = index.row()
        col = index.column()-1

        entity_values = self.getInstanceAt(row)
        column_name = self.columns[col]


        if role == QtCore.Qt.DisplayRole:
            if col == -1:
                return self.entity_titles[row]

            try:
                if 'IPC' not in column_name:
                    return "{:>,d}".format(entity_values[column_name])
                else:
                    return "{:>.3f}".format(entity_values[column_name])
            except:
                return entity_values[column_name]
        elif role == QtCore.Qt.TextAlignmentRole:
            return QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter

        else:
            return None

    def headerData(self, section, orientation, role):
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                if section == 0:
                    return "Test name"
                else:
                    return self.columns[section-1]
        else:
            return None

    def getInstanceAt(self, row):
        entity_title = self.entity_titles[row]
        return self.values[entity_title]

    def sort(self, column, order):
        reverse_order = False
        column = column - 1

        if order == QtCore.Qt.DescendingOrder:
            reverse_order = True

        l = lambda title: self.values[title][self.columns[column]]

        self.beginResetModel()
        self.entity_titles.sort(key=l, reverse=reverse_order)
        self.endResetModel()

class ExecSizeQueryDataModel(PerfQueryDataModel):
    pass

class ExecTimeQueryDataModel(PerfQueryDataModel):
    pass
