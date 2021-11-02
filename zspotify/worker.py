import sys
import traceback
from PyQt5.QtCore import QObject, pyqtSignal, QRunnable
from const import TRACKS, ARTISTS, ALBUMS, PLAYLISTS


class WorkerSignals(QObject):
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    update = pyqtSignal(float)
    result = pyqtSignal(object)


class Worker(QRunnable):

    def __init__(self, fn, *args, **kwargs):
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()
        if "update" in self.kwargs.keys():
            self.signals.update.connect(self.kwargs["update"])

    def run(self):
        try:
            if "update" in self.kwargs.keys():
                result = self.fn(
                    self.signals.update.emit, *self.args, **self.kwargs
                )
            else:
                result = self.fn(
                 *self.args, **self.kwargs
                )
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)  # Return the result of the processing
        finally:
            self.signals.finished.emit()
