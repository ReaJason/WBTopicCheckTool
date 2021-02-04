from PyQt5.QtGui import QImage, QIcon, QPixmap
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QDialog, QLabel, QHBoxLayout
from settings import ICON_PATH
from core.scan_login import ScanPicThread

__author__ = "ReaJason"
__date__ = "2021年2月4日"
__site__ = "https://reajason.top"
__email__ = "reajason@163.com"


class ScanImage(QDialog):
    signal = pyqtSignal(dict)

    def __init__(self, session, qr_dict):
        super().__init__()
        self.qrid = qr_dict['qrid']
        self.setWindowTitle('扫码登录')
        self.setWindowIcon(QIcon(ICON_PATH))
        layout = QHBoxLayout()
        self.pic_lb = QLabel()
        res = session.get(qr_dict['img_url']).content
        img = QImage.fromData(res)
        self.pic_lb.setPixmap(QPixmap.fromImage(img))
        layout.addWidget(self.pic_lb)
        self.setLayout(layout)
        self.scan_check_t = ScanPicThread(self, session, self.qrid)
        self.scan_check_t.start()
        self.scan_check_t.scan_signal.connect(self.emit_signal)
    
    def emit_signal(self, login_dict):
        self.signal.emit(login_dict)
        self.close()
