
from PyQt5.QtWidgets import QTreeWidgetItem
from PyQt5.QtCore import pyqtSignal, QObject
from item import Item


class ItemTree(QObject):

    doubleClicked = pyqtSignal(Item)
    itemChanged = pyqtSignal(Item, list, list)
    onSelected = pyqtSignal(list)

    def __init__(self, tree, tree_widget_builder = None):
        super().__init__()
        self.tree = tree
        self.treeItems = []
        self.selected_item = None
        if tree_widget_builder == None:
            tree_widget_builder = lambda track: QTreeWidgetItem([str(track.index), track.title, track.artists, \
                track.album, str(track.duration), track.release_date])
        self.tree_widget_builder = tree_widget_builder
        self.init_signals()

    def add_item(self, item):
        widget_item = self.tree_widget_builder(item)
        tree_item = TreeItem(item, widget_item)
        self.treeItems.append(tree_item)
        self.tree.addTopLevelItem(widget_item)


    def set_items(self, items):
        if items == None or len(items) <= 0: return
        self.tree.clear()
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

    def select(self):
        self.onSelected.emit(self.get_headers())
        if self.tree.topLevelItemCount() > 0:
            self.tree.setCurrentItem(self.tree.topLevelItem(0))

    def clear(self):
        self.treeItems = []
        self.selected_item = None
        self.tree.clear()


    def get_selected_item(self):
        tree_widget = self.tree.currentItem()
        if tree_widget:
            for treeItem in self.treeItems:
                if treeItem.is_matching_tree_item(tree_widget):
                    self.selected_item = treeItem.item
                    return self.selected_item
        elif len(self.treeItems):
            self.selected_item = self.treeItems[0]
            return self.selected_item
        if self.treeItems != None and len(self.treeItems) > 0: return self.treeItems[0].item
        return None

    def get_headers(self):
        headers = []
        for i in range(self.tree.columnCount()):
            headers.append(self.tree.headerItem().text(i))
        return headers

    def on_item_changed(self, widget_item, old):
        #self.itemChanged.emit()
        if widget_item == None: return
        self.selected_item = self.get_selected_item()
        headers = self.get_headers()
        labels = []
        for i in range(widget_item.columnCount()):
            labels.append(widget_item.text(i))
        self.itemChanged.emit(self.selected_item, headers, labels)

    def on_double_clicked(self,widget_item, item):
        item = self.get_selected_item()
        self.doubleClicked.emit(item)

    def init_signals(self):
        self.tree.currentItemChanged.connect(self.on_item_changed)
        self.tree.itemDoubleClicked.connect(self.on_double_clicked)




class TreeItem():
    def __init__(self, item, tree_widget_item):
        self.item = item
        self.tree_widget_item = tree_widget_item


    def is_matching_tree_item(self, tree_widget_item):
        if self.tree_widget_item == tree_widget_item:
            return True
        return False
