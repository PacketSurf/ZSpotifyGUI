import sys
import traceback
import logging
from PyQt5.QtCore import QObject, pyqtSignal, QRunnable
from const import TRACKS, ARTISTS, ALBUMS, PLAYLISTS

logger = logging.getLogger(__name__)

class WorkerSignals(QObject):
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    update = pyqtSignal(object)
    result = pyqtSignal(object)

class MusicSignals(WorkerSignals):
    update = pyqtSignal(float, int, int)

class Worker(QRunnable):
    #kwarg passed with key "update" is a callback function that gets connected to worker update signal
    #When using update the fn method must have a first parameter that will be a signal emit function
    def __init__(self, fn, *args, **kwargs):
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        if "signals" in self.kwargs:
            self.signals =self.kwargs["signals"]
        else: self.signals = WorkerSignals()
        if "update" in self.kwargs.keys():
            self.signals.update.connect(self.kwargs["update"])

    def run(self):
        try:
            logger.info("Attempting to start worker thread.")
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
            logger.error(f"{exctype} : {value} - {traceback.format_exc()}")
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)  # Return the result of the processing
        finally:
            self.signals.finished.emit()
