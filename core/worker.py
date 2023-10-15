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

    def __init__(self):
        self.file_path = ""
        self.stop = False           # stop 
        # self.reload = False          # start with a new file
        self.terminate = False      # kill thread
        self.timeout = 0.5

        self.processor = Core()
        super(MainThread, self).__init__()

    # def __del__(self):
    #     self.wait()

    def set_data(self, file_path=""):
        self.file_path = file_path
        self.processor.read(self.file_path)

    def kill(self):
        self.terminate = True

    def pause(self):
        self.stop = True

    def ready(self):
        self.stop = False

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
            self.message.emit("Data loaded!\n\n")

            for result in self.processor.release(urls):
                if self.stop:
                    break
                if not self.stop:
                    message, progress = self.postprocess(result=result)
                    self.message.emit(message)
                    self.progress.emit(progress)
