from PyQt5.QtWidgets import QTreeWidgetItem, QMenu, QApplication, QTreeWidget
from PyQt5.QtCore import Qt, pyqtSignal, QObject
from item import Item
from utils import delete_file

class ItemTree:

    def __init__(self, tree, tree_widget_builder = None, can_play = True):
        self.tree = tree
        self.items = []
        self.tree_items = {}
        self.selected_item = None
        self.load_function = None
        self.can_play = can_play
        self.signals = ItemTreeSignals()
        if tree_widget_builder == None:
            tree_widget_builder = lambda track: QTreeWidgetItem([str(track.index), track.title, track.artists, \
                track.album, str(track.duration), track.release_date])
        self.tree_widget_builder = tree_widget_builder
        self.init_signals()

    def load_content(self):
        try:
            if self.load_function: self.load_function()
        except Exception as e:
            logging.error(e)


    def add_item(self, item):
        widget_item = self.tree_widget_builder(item)
        self.items.append(item)
        self.tree_items[item] = widget_item
        self.tree.addTopLevelItem(widget_item)

    def remove_item(self, item):
        self.items.remove(item)
        if item in self.tree_items:
            index = self.item_index(item)
            if index != -1 : self.tree.takeTopLevelItem(index)
            self.tree_items.pop(item, None)

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
            logging.error(e)
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
        if not widget_item: return
        self.selected_item = self.get_selected_item()
        if not self.selected_item: return
        headers = self.get_headers()
        labels = []
        for i in range(widget_item.columnCount()):
            labels.append(widget_item.text(i))
        self.signals.itemChanged.emit(self.selected_item, headers, labels)

    def on_double_clicked(self,widget_item, item):
        item = self.get_selected_item()
        if item:
            self.tree.itemClicked.emit(widget_item, self.item_index(item))
            self.signals.doubleClicked.emit(item, self)

    def on_delete_item(self):
        self.signals.onDeleted.emit(self.selected_item, self.tree)
        if not self.selected_item.path == "":
            delete_file(self.selected_item.path)
        if not self.selected_item: return
        self.remove_item(self.selected_item)


    def on_download_item(self):
        if not self.selected_item or self.selected_item.downloaded: return
        self.signals.onDownloadQueued.emit(self.selected_item)

    def on_listen_queue(self):
        if not self.selected_item: return
        self.signals.onListenQueued.emit(self.selected_item)

    def on_context_menu(self, pos):
        if not self.selected_item: return
        node = self.tree.mapToGlobal(pos)
        self.popup_menu = QMenu(None)
        if self.selected_item.downloaded:
            self.popup_menu.addAction("Add to listen queue", self.on_listen_queue)
        else:
             self.popup_menu.addAction("Add to download queue", self.on_download_item)
        if self.selected_item.downloaded:
            self.popup_menu.addSeparator()
            self.popup_menu.addAction("Delete", self.on_delete_item)
        self.popup_menu.exec_(self.tree.mapToGlobal(pos))

    def init_signals(self):
        self.tree.currentItemChanged.connect(self.on_item_changed)
        self.tree.itemDoubleClicked.connect(self.on_double_clicked)
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.on_context_menu)

class ItemTreeSignals(QObject):
    doubleClicked = pyqtSignal(Item, ItemTree)
    itemChanged = pyqtSignal(Item, list, list)
    onSelected = pyqtSignal(list)
    onDeleted = pyqtSignal(Item, QTreeWidget)
    onListenQueued = pyqtSignal(Item)
    onDownloadQueued = pyqtSignal(Item)
