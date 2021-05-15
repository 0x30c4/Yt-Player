from PyQt5.QtCore import Qt, QThread, pyqtSignal
from time import sleep

class Thread(QThread):
    retc = pyqtSignal(dict)
    streamObj = None
    sn = ''
    def run(self):
        self.streamObj.songNameOrUrl = self.sn
        for i in self.streamObj.play():
            self.retc.emit(i)
        self.retc.emit({})
        