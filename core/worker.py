import time

from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QWidget, QPushButton, QProgressBar, QVBoxLayout, QApplication

from core.processor import Core




# for multi thread
# from PyQt5.QtCore import QRunnable, QThreadPool
# https://www.pythonguis.com/tutorials/multithreading-pyqt-applications-qthreadpool/



class MainThread(QThread):

    progress = pyqtSignal(int)
    message = pyqtSignal(str)
    reset = pyqtSignal(bool)

    def __init__(self, cfgs):
        self.file_path = ""
        self.stop = False           # stop 
        # self.reload = False          # start with a new file
        self.terminate = False      # kill thread
        self.timeout = 0.5
        self.environ = "prod"

        self.processor = Core()
        super(MainThread, self).__init__()

    # def __del__(self):
    #     self.wait()

    def status(self):
        return f"Terminal {self.terminate} | Stop {self.stop}"

    def set_cfg(self, cfgs):
        self.environ = cfgs.get("env")

    def set_data(self, file_path=""):
        self.file_path = file_path
        self.processor.read(self.file_path)
        self.message.emit("Data loaded!")
        print('* PROCESS SET DATA')

    def empty_data(self):
        self.file_path = ""
        self.processor = Core()
        print('\n* PROCESS RESET')

    def kill(self):
        self.terminate = True
        print('* PROCESS KILL')

    def pause(self):
        self.stop = True
        print('* PROCESS PAUSE')

    def ready(self):
        self.stop = False
        print('* PROCESS READY')

    def get_data_info(self):
        return self.processor.data_info()

    def postprocess(self, result):
        progress = None
        if result.get("success"):
            message = f"URL-{result.get('url')}.\n{result.get('message')}"
            progress = result.get("step")
        else:
            message = f"URL-{result.get('url')}.\n{result.get('message')}"

        return message, progress
    
    def run(self):
        while True:
            if self.terminate:
                break
            if self.stop:
                time.sleep(self.timeout)
                continue

            urls = self.processor.urls

            if self.environ == "dev":
                self.message.emit("Starting...!")
                self.message.emit("*"*30)
                for result in self.processor.test_release(urls):
                    if self.stop:
                        break
                    if not self.stop:
                        message, progress = self.postprocess(result=result)
                        self.message.emit(message)
                        self.progress.emit(progress)
                self.stop = True
                self.message.emit("*"*30)
                self.reset.emit(True)
            else:
                self.message.emit("Starting...!")
                self.message.emit("*"*30)
                for result in self.processor.release(urls):
                    if self.stop:
                        break
                    if not self.stop:
                        message, progress = self.postprocess(result=result)
                        self.message.emit(message)
                        self.progress.emit(progress)
                self.stop = True
                self.message.emit("*"*30)
                self.reset.emit(True)
