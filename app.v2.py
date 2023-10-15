#!/usr/bin/python
import sys
import time

from PyQt5 import uic, QtGui
from PyQt5.QtGui import QIcon, QTextCursor
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QToolBar, QFileDialog, QAction, QMessageBox, QDesktopWidget
from PyQt5.QtCore import QCoreApplication, Qt, QT_VERSION_STR, PYQT_VERSION_STR
print('> QT version: ', QT_VERSION_STR)
print('> PyQT version: ', PYQT_VERSION_STR)

from core.worker import MainThread



class Ui(QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('view/main.ui', self)
        self._adjust_screen()
        self._createActions()
        self._createMenuBar()
        self._connectActions()
        self._create_hiden_actions()

        self.thread = MainThread()
        self.thread.progress.connect(self.update_progress)
        self.thread.message.connect(self.update_log)

        self.show()

    def _adjust_screen(self):
        qtRectangle = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())

    def _createMenuBar(self):
        menuBar = self.menuBar()
        menuBar.setStyleSheet("background-color: rgb(192, 191, 188);")
        # add_icon = QtGui.QIcon("resources/add-icon.png")
        # self.openFile = menuBar.addMenu(add_icon, "&Open File")
        self.openFile = menuBar.addMenu("&File")
        self.openFile.addAction(self.openAction)
        help_icon = QtGui.QIcon("resources/help-icon.png")
        self.helpMenu = menuBar.addMenu(help_icon, "&Help")
        self.helpMenu.addAction(self.aboutAction)

    def _createActions(self):
        self.openAction = QAction(QIcon("resources/add-icon.png"), "&Open...", self)
        self.openAction.setShortcut("Ctrl+O")
        self.aboutAction = QAction("&About me", self)

    def _connectActions(self):
        self.openAction.triggered.connect(self.openf)
        self.aboutAction.triggered.connect(self.show_about_me)

    def _create_hiden_actions(self):
        self.openFileButton.clicked.connect(self.openf)
        self.runButton.clicked.connect(self.runThread)
        self.stopButton.clicked.connect(self.stopThread)
        self.pbar.setValue(0)
        self.available(status=True)
        
        self.link_counter_text.setReadOnly(True)
        self.domain_list_text.setReadOnly(True)
        self.message_detail.verticalScrollBar().setValue(self.message_detail.verticalScrollBar().minimum())

    def available(self, status=False, ready=False, running=False):
        """
            Params:
                - status: system status
                - ready: ready to run
                - running: -> running
        """
        print("UPDATE STATUS ", status, ready)
        self.openFileButton.setEnabled(status)
        if not status:
            self.openFileButton.setStyleSheet("background-color: gray;")
        else:
            self.openFileButton.setStyleSheet("background-color: violet;")

        self.runButton.setEnabled(ready)
        if not ready:
            self.runButton.setStyleSheet("background-color: gray;")
        else:
            self.thread.ready()
            self.runButton.setStyleSheet("background-color: green;")

        self.stopButton.setEnabled(running)
        if not running:
            self.stopButton.setStyleSheet("background-color: gray;")
        else:
            self.stopButton.setStyleSheet("background-color: rgb(255, 163, 72);")

    def openf(self):
        path = QFileDialog.getOpenFileName(self, 'Open a file', '', 'All Files (*.*)')
        self.link_counter_text.setText("")
        self.domain_list_text.setText("")
        # self.thread.set_data(self.filePath.toPlainText())
        if path != ('', ''):
            self.available(ready=True)
            self.filePath.setText(path[0])
            self.thread.set_data(path[0])
            self.show_data()

    def show_data(self):
        info = self.thread.get_data_info()
        
        summary = ""
        if info.get("length"):
            summary += f"Total ({str(info.get('length'))}) | "
        if info.get("live_urls"):
            summary += f"Live ({str(len(info.get('live_urls')))}) | "
        if info.get("die_urls"):
            summary += f"Die ({str(len(info.get('live_urls')))})"
            self.update_log("\n\nLINK DIED")
            self.update_log("\n".join([url for url in info.get("die_urls")]))
            self.update_log("\n\n\n")

        self.link_counter_text.setText(summary)
            
        if info.get("domain_list"):
            self.domain_list_text.setText(", ".join([d for d in info.get("domain_list")]))

    def runThread(self):
        self.available(running=True)
        self.process()

    def stopThread(self):
        self.thread.pause()
        self.update_progress(0)
        self.update_log("\n\n*** Terminated!")
        self.available(status=True)
        print('stopped')

    def show_about_me(self):
        self.show_message(title="Lời nhắn", message="Cảm ơn bạn!", details="From tuanlh")

    def update_progress(self, msg):
        if msg:
            self.pbar.setValue(int(msg))
        # if self.pbar.value() == 99:
        #     self.pbar.setValue(0)
        #     self.openFileButton.setEnabled(True)

    def update_log(self, msg):
        self.message_detail.insertPlainText(msg + "\n")

    def show_message(self, title="Notification", message="", details=""):
        print('show msg')
        msg = QMessageBox()
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setDetailedText(details)
        msg.exec_()

    def keyPressEvent(self, event):
        """Close application from escape key.
        results in QMessageBox dialog from closeEvent, good but how/why?
        """
        if event.key() == Qt.Key_Escape or event.key() == Qt.Key_Q:
            self.thread.kill()
            time.sleep(0.3)
            self.close()

    def process(self):
        # self.show_message(message=file_path)
        self.thread.start()
        



def main():
	app = QApplication(sys.argv)
	w = Ui()
	w.move(500, 300)
	w.setWindowTitle('Auto Tool')
	sys.exit(app.exec())


if __name__ == '__main__':
    main()
