from PyQt5 import QtWidgets
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDialog, QApplication, QMainWindow, QFrame
from PyQt5.QtCore import Qt, QSize, QRect
from PyQt5.uic import loadUi
from os import name, system, chdir, remove, sys
from datetime import timedelta

from stream import Stream, path
from thread_ import Thread


UI_PATH = 'UI'
PATH_SEP = "/"
if name == 'nt':
    PATH_SEP = "\\"

UI_FILES = {
    "main": r"UI\MainUi.ui",
    "queue": r"UI\Add_queue.ui"
}

class MainGuiUi(QMainWindow):
    def __init__(self):
        super(MainGuiUi, self).__init__()
        loadUi(UI_FILES["main"], self)

        # chdir("C:\\Users\\sami\\Desktop\\tmp\\Yt-Player")

        self.imgPaths = {
            "loop_0": r"img\loop_off.png",
            "loop_1": r"img\loop_on.png",
            "next":   r"img\next.png",
            "prev":   r"img\prev.png",
            "play":   r"img\play.png",
            "pause":   r"img\pause.png",
            "search": r"img\search.png",
            "stop":   r"img\stop.png"
        }

        self.isPause = False
        self.isRepeat = False
        self.isStop = False

        self.streamobj = Stream()

        self.songs = {}
        self.songCount = 0


        self.playB.clicked.connect(self.Play)
        self.playB.setIcon(QIcon(self.imgPaths["play"]))
        self.playB.setIconSize(QSize(90, 90))


        # self.prevB.clicked.connect(self.Play)
        self.prevB.setIcon(QIcon(self.imgPaths["prev"]))
        self.prevB.setIconSize(QSize(90, 90))

        # self.nextB.clicked.connect(self.Play)
        self.nextB.setIcon(QIcon(self.imgPaths["next"]))
        self.nextB.setIconSize(QSize(90, 90))


        self.stopB.clicked.connect(self.Stop)
        self.stopB.setIcon(QIcon(self.imgPaths["stop"]))
        self.stopB.setIconSize(QSize(90, 90))

        self.loopB.clicked.connect(self.Repeat)
        self.loopB.setIcon(QIcon(self.imgPaths["loop_0"]))
        self.loopB.setIconSize(QSize(90, 90))


        self.add_to_qB.clicked.connect(self.addToQueue)

        self.tray_icon = QtWidgets.QSystemTrayIcon(self)
        self.tray_icon.activated.connect(self.onTrayIconActivated)
        self.tray_icon.setIcon(QIcon("favicon.ico"))


        self.play_action = QtWidgets.QAction("Play", self)
        self.stop_action = QtWidgets.QAction("Stop", self)
        self.next_action = QtWidgets.QAction("Next Song", self)
        self.prev_action = QtWidgets.QAction("Previous Song", self)
        self.repeat_action = QtWidgets.QAction("Repeat Current Song", self)


        self.play_action.setIcon(QIcon(self.imgPaths["play"]))
        self.stop_action.setIcon(QIcon(self.imgPaths["stop"]))
        self.next_action.setIcon(QIcon(self.imgPaths["next"]))
        self.prev_action.setIcon(QIcon(self.imgPaths["prev"]))
        self.repeat_action.setIcon(QIcon(self.imgPaths["loop_0"]))


        self.show_hide_action = QtWidgets.QAction("Show/Hide", self)
        self.quit_action = QtWidgets.QAction("Exit", self)


        self.play_action.triggered.connect(self.Play)
        self.stop_action.triggered.connect(self.Stop)
        self.next_action.triggered.connect(self.Next)
        self.prev_action.triggered.connect(self.Prev)
        self.play_action.triggered.connect(self.Play)
        self.repeat_action.triggered.connect(self.Repeat)
        self.show_hide_action.triggered.connect(self.showHideB)
        self.quit_action.triggered.connect(self.app_exit)


        self.tray_menu = QtWidgets.QMenu()
        self.tray_menu.addAction(self.play_action)
        self.tray_menu.addAction(self.stop_action)
        self.tray_menu.addAction(self.next_action)
        self.tray_menu.addAction(self.prev_action)

        self.tray_menu.addAction(self.repeat_action)


        self.tray_menu.addAction(self.show_hide_action)
        self.tray_menu.addAction(self.quit_action)
        self.tray_icon.setContextMenu(self.tray_menu)
        self.tray_icon.show()
        self.wdh = ''

        self.progressBar.setTextVisible(False)
        self.progressBar.setValue(0)

    def onTrayIconActivated(self, reason):

        if self.isVisible() and QtWidgets.QSystemTrayIcon.DoubleClick == reason:
            self.wdh.setVisible(False)
        elif not self.isVisible() and QtWidgets.QSystemTrayIcon.DoubleClick == reason:
            self.wdh.setVisible(True)

    def showHideB(self):
        if self.isVisible():
            self.wdh.setVisible(False)
        elif not self.isVisible():
            self.wdh.setVisible(True)

    def app_exit(self):
        self.streamobj.streamCtl("stop")
        sys.exit()

    def Play(self, rp=False):
        song_name = self.songName.text()
        if len(self.songs.keys()) == 0 or self.isStop or rp:
            print("REPEAT ", self.isRepeat)
            self.isStop = False
            self.songCount = self.songCount + 1
            self.songs.update({self.songCount: song_name})
            self.thread = Thread()
            self.thread.streamObj = self.streamobj
            self.thread.sn = song_name
            self.thread.retc.connect(self.setProgressBarV)
            self.thread.start()
            self.status.setText(f"Now Playing\n{song_name}")

            self.playB.setIcon(QIcon(self.imgPaths["pause"]))
            self.play_action.setIcon(QIcon(self.imgPaths["pause"]))


        elif self.isPause and not self.isStop and not len(self.songs.keys()) == 0:
            self.playB.setIcon(QIcon(self.imgPaths["pause"]))
            self.play_action.setIcon(QIcon(self.imgPaths["pause"]))
            self.play_action.setText("Play")
            self.isPause = False
            self.streamobj.streamCtl("resume")
            print("Resume")
        elif not self.isStop and not self.isPause and not len(self.songs.keys()) == 0:
            self.playB.setIcon(QIcon(self.imgPaths["play"]))
            self.play_action.setIcon(QIcon(self.imgPaths["play"]))
            self.play_action.setText("Resume")
            self.streamobj.streamCtl("pause")
            self.isPause = True
            print("Pause")


    def setProgressBarV(self, v):
        if v == {}:
            self.playB.setIcon(QIcon(self.imgPaths["play"]))
            self.play_action.setIcon(QIcon(self.imgPaths["play"]))
            self.progressBar.setValue(0)
            self.isStop = True
            self.durationL.setText('')
            self.currentTimeL.setText('')
            return

        p = (v['CS'] / v['TS']) * 100

        ct = str(timedelta(seconds=v["TS"]))
        du = str(timedelta(seconds=v['CS']))

        self.durationL.setText(ct)

        self.currentTimeL.setText(du)



        self.progressBar.setValue(p)
        if v["TS"] - 2 == v["CS"]:
            self.isPause = False
            self.isStop = False
            if self.isRepeat:
                self.progressBar.setValue(0)
                self.durationL.setText('')
                self.currentTimeL.setText('')
                self.streamobj.streamCtl("stop")
                self.Play(rp=True)


    def Next(self):
        print("next")

    def Prev(self):
        print("Prev")

    def Repeat(self):
        if self.isRepeat:
            self.loopB.setIcon(QIcon(self.imgPaths["loop_0"]))
            self.repeat_action.setIcon(QIcon(self.imgPaths["loop_0"]))
            self.repeat_action.setText("Repeat Current Song")
            self.isRepeat = False
            print("Repeat 0")
        else:
            self.loopB.setIcon(QIcon(self.imgPaths["loop_1"]))
            self.repeat_action.setIcon(QIcon(self.imgPaths["loop_1"]))
            self.repeat_action.setText("Off Repeating")
            self.isRepeat = True
            print("Repeat 1")

    def Stop(self):
        self.isStop = True
        self.streamobj.streamCtl("stop")
        self.playB.setIcon(QIcon(self.imgPaths["play"]))
        self.play_action.setIcon(QIcon(self.imgPaths["play"]))
        self.play_action.setText("Play")
        self.progressBar.setValue(0)
        print("Stopped")

    def Cpb(self):
        system('start https://0x30c4.github.io')
        system('start https://twitter.com/0x30c4')

    def addToQueue(self):
        addtoq = AddToQueue()
        widget.addWidget(addtoq)
        widget.setCurrentIndex(widget.currentIndex()+1)

    # border: 2px solid #555;
    # border-radius: 20px;

class AddToQueue(QMainWindow):
    def __init__(self):
        super(AddToQueue, self).__init__()
        loadUi(UI_FILES["queue"], self)

        self.add2qB.clicked.connect(self.addToQueue)

    def addToQueue(self):
        sq = []
        for l in self.qsi.toPlainText().split("\n"):
            if bool(l):
                sq.append(l)

        print(sq)
        main = MainGuiUi()
        widget.addWidget(main)
        widget.setCurrentIndex(widget.currentIndex()+1)

def n():
    widget.setVisible(False)


if __name__ == "__main__":

    app = QApplication([])

    mainwindow = MainGuiUi()

    widget = QtWidgets.QStackedWidget()
    widget.addWidget(mainwindow)

    mainwindow.wdh = widget

    widget.setWindowTitle("Youtube Player")
    widget.setFixedWidth(330)
    widget.setFixedHeight(400)

    widget.show()
    widget.setWindowIcon(QIcon('favicon.ico'))

    app.setQuitOnLastWindowClosed(False)
    app.lastWindowClosed.connect(n)
    # widget.closeEvent(n)

    app.exec_()
