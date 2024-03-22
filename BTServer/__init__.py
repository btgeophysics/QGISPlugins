from .server import *
from PyQt5.QtWidgets import QAction, QMessageBox
from threading import Thread, Event
import time
from .commands import execute_commands
import json

from qgis.core import QgsTask, QgsMessageLog, Qgis, QgsApplication
from PyQt5.QtCore import QObject, QThread, pyqtSignal

def classFactory(iface):
    return BTServerPlugin(iface)


def waitForEvent(inp,event = None):

    QgsMessageLog.logMessage(f"waitForCommand: {inp}",
                                 'BTServer', Qgis.Info)
    # time.sleep(5)

    # return {"status":"sleep 5"}
    

    # while not event.isSet():
    #     event_is_set = event.wait()

    #     if event_is_set:
    #         return {"status":"successXX"}
    #     else:
    #         return {"status":"failedXX"}

    return {"status":"successXX"}

def eventCompleted(result=None):
    QgsMessageLog.logMessage(f"Event completed: {result}",'BTServer', Qgis.Info)
    print(result)
    QMessageBox.information(None, 'BTServer plugin', 'eventCompleted')
    pass
def cmdEvent(inp):
    QgsMessageLog.logMessage(f"cmdEvent: {inp}",'BTServer', Qgis.Info)
    try:
        jinp = json.loads(inp)
        execute_commands(jinp)
    except Exception as err:
        QgsMessageLog.logMessage(f"cmdEvent: failed: {err}",'BTServer', Qgis.Info)
        pass

class BTServerPlugin:
    def __init__(self, iface):
        self.iface = iface
        self.thread = None
        self.worker = None

    def initGui(self):
        self.action = QAction('Go!', self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        self.iface.addToolBarIcon(self.action)

    def unload(self):
        self.iface.removeToolBarIcon(self.action)
        del self.action

    def run(self):

        # daemon = Thread(target=start,args = (self.event,payload,), daemon=True, name='BTServer')
        # daemon.start()
        self.thread = QThread()
        self.worker = ServerWorker()
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit) # quit thread when worker finishes work
        self.worker.finished.connect(self.worker.deleteLater) # delete worker objects when work is done
        self.thread.finished.connect(self.thread.deleteLater) # delete thread objects when work is done
        self.worker.cmdevt.connect(cmdEvent)
        # self.worker.progress.connect(waitForEvent)
        self.worker.finished.connect(eventCompleted)

        self.thread.start()


        QMessageBox.information(None, 'BTServer plugin', 'Background server has been started')


class Worker(QObject):
    finished = pyqtSignal()
    cmdevt = pyqtSignal(object)
    # progress = pyqtSignal(int)

    def run(self):
        """Server process"""
        for kk in range(10):
            time.sleep(1)
            self.cmdevt.emit({"type":"atype","data":kk})
            # self.progress.emit(kk + 1)
        self.finished.emit()