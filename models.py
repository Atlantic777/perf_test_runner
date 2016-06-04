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

    def columnCount(self, index=None):
        if self.entity is None:
            return 0
        else:
            cols =  max([len(opts) for opts in self.entity.instances.values()])
            return cols # the one for compiler name

    def rowCount(self, index=None):
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

class QueryDataTableModel(QAbstractTableModel):
    def __init__(self):
        super().__init__()

        self.entity_titles = sorted([entity.source.name for entity in self.entities])

    def columnCount(self, index=None):
        cnt =  len(self.get_visible_columns()) + 1
        return cnt

    def rowCount(self, parent=None):
        count = len(self.entity_manager.entityList)
        return count

    def data(self, index, role):
        row = index.row()
        col = index.column() - 1
        columns = self.get_visible_columns()

        if role == QtCore.Qt.DisplayRole:
            if col == -1:
                return self.entity_titles[row]

            entity_values = self.getInstanceAt(row)
            column_name = columns[col][0]

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
                    return self.get_visible_columns()[section-1][0]
        else:
            return None

    def getInstanceAt(self, row):
        entity_title = self.entity_titles[row]
        return self.query_data[entity_title]

    def getEntityAt(self, row):
        entity_title = self.entity_titles[row]
        return self.entity_manager.get_entity(entity_title)

    def sort(self, column, order):
        reverse_order = False
        column = column - 1
        column_titles = [col[0] for col in self.get_visible_columns()]

        if order == QtCore.Qt.DescendingOrder:
            reverse_order = True

        l = lambda title: self.query_data[title][column_titles[column]]

        self.beginResetModel()
        self.entity_titles.sort(key=l, reverse=reverse_order)
        self.endResetModel()

class PerfEstModel(QAbstractTableModel):
    column_headers = [
        'function',
        'basic block',
        'entry freq',
        'block freq',
        'norm freq',
        'i count',
        'val',
    ]

    def __init__(self, result):
        super().__init__()
        self.result = result
        self.d = result.parsed_data['freq']

        self.build_fbb_pairs()

        (f, b) = self.pairs[0]
        self.column_titles = sorted(self.d[f][b].keys())

    def build_fbb_pairs(self):
        f = sorted(self.d.keys())

        self.pairs = []
        for function in f:
            for bb_name in sorted(self.d[function].keys()):
                self.pairs.append( (function, bb_name) )

    def headerData(self, section, orientation, role):
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return self.column_headers[section]
            if orientation == QtCore.Qt.Vertical:
                return section + 1

    def columnCount(self, index=None):
        return len(self.column_headers)

    def rowCount(self, index=None):
        return len(self.pairs)

    def data(self, index, role):
        if role == QtCore.Qt.DisplayRole:
            entry =  self.get_entry_for_row(index.row())
            fmt = lambda v : "{:,.2f}".format(float(v))

            c = index.column()
            if c == 0:
                return self.pairs[index.row()][0]
            elif c == 1:
                return self.pairs[index.row()][1]
            elif c == 2:
                return fmt(entry['entry_freq'])
            elif c == 3:
                return fmt(entry['block_freq'])
            elif c == 4:
                return fmt(entry['norm_freq'])
            elif c == 5:
                return fmt(entry['cnt'])
            elif c == 6:
                return fmt(entry['val'])
            else:
                return "None"
        elif role == QtCore.Qt.TextAlignmentRole and index.column() >= 2:
            return QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter

    def get_entry_for_row(self, row):
        (function, block) = self.pairs[row]
        return self.d[function][block]
