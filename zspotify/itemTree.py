from PyQt5.QtWidgets import QTreeWidgetItem
from PyQt5.QtCore import pyqtSignal, QObject
from item import Item


class ItemTree:


    def __init__(self, tree, tree_widget_builder = None):

        self.tree = tree
        self.items = []
        self.tree_items = {}
        self.selected_item = None
        self.signals = ItemTreeSignals()
        if tree_widget_builder == None:
            tree_widget_builder = lambda track: QTreeWidgetItem([str(track.index), track.title, track.artists, \
                track.album, str(track.duration), track.release_date])
        self.tree_widget_builder = tree_widget_builder
        self.init_signals()


    def add_item(self, item):
        widget_item = self.tree_widget_builder(item)
        self.items.append(item)
        self.tree_items[item] = widget_item
        self.tree.addTopLevelItem(widget_item)


    def set_items(self, items):
        if items == None or len(items) <= 0: return
        self.clear()
        for item in items:
            self.add_item(item)

    def set_header_item(self, item):
        try:
            widget_item = self.tree_widget_builder(item)
            self.tree.setHeaderItem(widget_item)
        except Exception as e:
            print(e)

    def set_header_spacing(self, *args):
        for i in range(self.tree.columnCount()):
            if i < len(args):
                if args[i] < 0: continue
                self.tree.header().resizeSection(i, args[i])
            else: break

    def focus(self):
        self.signals.onSelected.emit(self.get_headers())
        if self.tree.topLevelItemCount() > 0:
            self.tree.setCurrentItem(self.tree.topLevelItem(0))

    def select_item(self, item):
        index = self.item_index(item)
        self.select_index(index)

    def select_index(self, index):
        if len(self.items) == 0 or index >= len(self.items) or index < 0: return None
        widget_item = self.tree.topLevelItem(index)
        self.tree.setCurrentItem(widget_item)
        return self.get_selected_item()

    def item_index(self, item):
        if not self.tree_items or len(self.tree_items) <= 0: return -1
        if not item in self.tree_items: return -1
        for i in range(self.tree.topLevelItemCount()):

            if self.tree.topLevelItem(i) == self.tree_items[item]:
                return i
        return -1

    def current_item_index(self):
        item = self.get_selected_item()
        if not item: return -1
        return self.item_index(item)

    def clear(self):
        self.items = []
        self.tree_items = {}
        self.selected_item = None
        self.tree.clear()


    def get_selected_item(self):
        tree_widget = self.tree.currentItem()
        if tree_widget:
            for item in self.items:
                if self.tree_items[item] == tree_widget:
                    self.selected_item = item
                    return self.selected_item
        elif len(self.treeItems):
            self.selected_item = self.items[0]
            return self.selected_item
        return None

    def get_headers(self):
        headers = []
        for i in range(self.tree.columnCount()):
            headers.append(self.tree.headerItem().text(i))
        return headers

    def count(self):
        return len(self.items)

    def on_item_changed(self, widget_item, old):
        #self.itemChanged.emit()
        if widget_item == None: return
        self.selected_item = self.get_selected_item()
        headers = self.get_headers()
        labels = []
        for i in range(widget_item.columnCount()):
            labels.append(widget_item.text(i))
        self.signals.itemChanged.emit(self.selected_item, headers, labels)

    def on_double_clicked(self,widget_item, item):
        item = self.get_selected_item()
        self.signals.doubleClicked.emit(item, self)

    def init_signals(self):
        self.tree.currentItemChanged.connect(self.on_item_changed)
        self.tree.itemDoubleClicked.connect(self.on_double_clicked)

class ItemTreeSignals(QObject):
    doubleClicked = pyqtSignal(Item, ItemTree)
    itemChanged = pyqtSignal(Item, list, list)
    onSelected = pyqtSignal(list)
