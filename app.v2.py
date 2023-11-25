#!/usr/bin/python
import os
import json
import sys
import time

from PyQt5 import uic, QtGui
from PyQt5.QtGui import QIcon, QTextCursor
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QToolBar, QFileDialog, QAction, QMessageBox, QDesktopWidget
from PyQt5.QtCore import QCoreApplication, Qt, QT_VERSION_STR, PYQT_VERSION_STR
# print('> QT version: ', QT_VERSION_STR)
# print('> PyQT version: ', PYQT_VERSION_STR)

from core.worker import MainThread

ROOT_DATA_DIR = "./app/data"
if not os.path.isdir(ROOT_DATA_DIR):
    os.makedirs(ROOT_DATA_DIR, exist_ok = True)



class Ui(QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('view/main.ui', self)
        self._adjust_screen()
        self._createActions()
        self._createMenuBar()
        self._connectActions()
        self._create_hiden_actions()

        cfgs = self.load_configure()

        self.thread = MainThread(cfgs)
        self.thread.progress.connect(self.update_progress)
        self.thread.message.connect(self.update_log)
        self.thread.reset.connect(lambda: self.available(status=True))

        self.available(status=True)
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
        self.cfg_path = os.path.join(ROOT_DATA_DIR, "cfg.json")
        self.openFileButton.clicked.connect(self.openf)
        self.validateButton.clicked.connect(self.validate)
        self.runButton.clicked.connect(self.runThread)
        self.stopButton.clicked.connect(self.stopThread)
        self.resetButton.clicked.connect(lambda: self.available(status=True))
        self.pbar.setValue(0)

        self.save_button.clicked.connect(self.save_configure)
        
        self.link_counter_text.setReadOnly(True)
        self.domain_list_text.setReadOnly(True)
        self.message_detail.verticalScrollBar().setValue(self.message_detail.verticalScrollBar().minimum())

    def available(self, status=False, ready=False, running=False):
        """
            Params:
                - stupdate_logatus: system status
                - ready: ready to run
                - running: -> running
        """
        print("UPDATE STATUS ", status, ready, running)

        ## OPEN button
        self.openFileButton.setEnabled(status)
        if status:
            self.thread.pause()
            self.thread.empty_data()
        if not status:
            self.openFileButton.setStyleSheet("background-color: gray;")
        else:
            self.openFileButton.setStyleSheet("background-color: violet;")

        ## RUN button
        self.runButton.setEnabled(ready)
        if not ready:
            self.runButton.setStyleSheet("background-color: gray;")
        else:
            self.thread.ready()
            self.runButton.setStyleSheet("background-color: green;")

        ## CHECK button
        self.validateButton.setEnabled(ready)
        if not ready:
            self.validateButton.setStyleSheet("background-color: gray;")
        else:
            self.validateButton.setStyleSheet("background-color: rgb(246, 97, 81);")

        ## STOP button
        self.stopButton.setEnabled(running)
        if not running:
            self.stopButton.setStyleSheet("background-color: gray;")
        else:
            self.stopButton.setStyleSheet("background-color: rgb(255, 163, 72);")

        ## RESET button
        if running:
            self.resetButton.setEnabled(False)
            self.resetButton.setStyleSheet("background-color: gray;")
        else:
            self.resetButton.setStyleSheet("background-color: rgb(51, 209, 122);")
        if status:
            self.resetButton.setEnabled(True)
        ## END

    def openf(self):
        path = QFileDialog.getOpenFileName(self, 'Open a file', '', 'All Files (*.*)')
        self.link_counter_text.setText("")
        self.domain_list_text.setText("")
        # self.thread.set_data(self.filePath.toPlainText())
        if path != ('', ''):
            self.available(ready=True)
            self.filePath.setText(path[0])
            self.update_log("Selected file!...")    
            self.thread.set_data(self.filePath.toPlainText())
        print('END OPEN >>', self.thread.status())

    def validate(self):
        self.update_log("Đang kiểm tra dữ liệu.....")
        if self.filePath.toPlainText():
            self.show_data()
        self.update_log("Validated file!...")
        print('END VALIDATE')

    def load_configure(self):
        cfgs = {}
        if hasattr(self, "cfg_path"):
            if os.path.isfile(self.cfg_path) and self.cfg_path.endswith('json'):
                with open(self.cfg_path, 'r', encoding='utf-8') as f:
                    cfgs = json.load(f)
                print(cfgs)
                self.tab_number.setText(cfgs.get("tab_number", 3))
                self.scroll_number.setText(cfgs.get("scroll_number", 5))
                self.interactive_time.setText(cfgs.get("interactive_time", 1))
                self.env.setText(cfgs.get("env", "dev"))
        
        self.update_log("Load configure successfully!...")
        print('END LOAD CONFIG')
        return cfgs

    def save_configure(self):
        tab_number = self.tab_number.text()
        scroll_number = self.scroll_number.text()
        interactive_time = self.interactive_time.text()
        env = self.env.text()

        def validate(text, ttype = 'int'):
            if ttype == 'int':
                try:
                    int(text)
                    return True, ""
                except:
                    return False, "Phải là số nguyên"
            
            if ttype == 'float':
                try:
                    float(text)
                    return True, ""
                except:
                    return False, "Phải là số thực"

        success, msg = validate(tab_number, 'int')
        if not success:
            self.show_message_popup("Cấu hình lỗi", f"Số Tab.{msg}")
            return
        success, msg = validate(scroll_number, 'int')
        if not success:
            self.show_message_popup("Cấu hình lỗi", f"Số lượt scroll.{msg}")
            return
        success, msg = validate(interactive_time, 'float')
        if not success:
            self.show_message_popup("Cấu hình lỗi", f"Thời gian tương tác.{msg}")
            return

        cfgs = {
            "tab_number": tab_number,
            "scroll_number": scroll_number,
            "interactive_time": interactive_time,
            "env": env
        }
        with open(self.cfg_path, 'w', encoding='utf-8') as f:
            json.dump(cfgs, f)
        self.show_message_popup("Thông báo", "Đã lưu cấu hình")
        print('END SAVE CONFIG')

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
        print('END SHOW DATA')

    def runThread(self):
        self.available(running=True)
        self.process()
        print('RUN PROCESS')

    def stopThread(self):
        self.thread.pause()
        self.update_progress(0)
        self.update_log("\n\n*** Terminated!")
        self.available(status=True)
        self.update_log('Done!')
        print('END STOP')

    def show_about_me(self):
        self.show_message_popup(title="Thông báo", message="Chào bạn", details="From tuanlh")

    def update_progress(self, msg):
        if msg:
            self.pbar.setValue(int(msg))
        # if self.pbar.value() == 99:
        #     self.pbar.setValue(0)
        #     self.openFileButton.setEnabled(True)

    def update_log(self, msg):
        self.message_detail.insertPlainText(f"\n{msg}\n")

    def show_message_popup(self, title="Notification", message="", details=""):
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
        # self.show_message_popup(message=file_path)
        self.thread.start()
        



def main():
	app = QApplication(sys.argv)
	w = Ui()
	w.move(500, 300)
	w.setWindowTitle('Auto Tool')
	sys.exit(app.exec())


if __name__ == '__main__':
    main()
