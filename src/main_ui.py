import sys
import ctypes
import requests

from PyQt5.QtGui import QIcon, QDesktopServices, QFont
from PyQt5.QtCore import QEvent, QUrl, Qt
from PyQt5.QtWidgets import QDialog, QLabel, QGridLayout, QPushButton, QComboBox, QMessageBox, QListWidget, QSpinBox, \
    QApplication, QStyleFactory, QWhatsThis

from core.super_topic_list import TopicListThread
from core.scan_login import QRCodeThread
from core.topic_check_in import CheckIn, super_topic_check_in
from src.login_ui import ScanImage
from settings import ICON_PATH

__author__ = "ReaJason"
__date__ = "2021年6月27日"
__site__ = "https://reajason.top"
__email__ = "reajason@163.com"


class MainWin(QDialog):
    def __init__(self):
        super(MainWin, self).__init__()
        self.setWindowTitle('微博超话工具 v2.1（By ReaJason）')
        
        # self.setFixedSize(500, 300)
        
        self.setWindowIcon(QIcon(ICON_PATH))
        
        font = QFont()
        font.setFamily('微软雅黑')
        self.setFont(font)
        
        self.cookie = None
        self.username = None
        self.super_topic_list = []
        
        layout = QGridLayout()
        
        lb1 = QLabel("昵称：")
        self.nick_lb = QLabel("等待登录...")
        
        lb2 = QLabel("签到间隔：")
        self.check_sleep = QSpinBox()
        self.check_sleep.setMinimum(1)
        
        self.super_topic_combo = QComboBox()
        self.super_topic_combo.addItem("超话列表")
        
        self.refresh_btn = QPushButton("刷新超话")
        self.refresh_btn.clicked.connect(self.refresh_topic_list)
        
        self.login_btn = QPushButton("扫码登录")
        self.login_btn.clicked.connect(self.scan_qr)
        
        self.check_all_btn = QPushButton("一键全签")
        self.check_all_btn.clicked.connect(self.check_in_all)
        
        self.check_one_btn = QPushButton("单签所选")
        self.check_one_btn.clicked.connect(self.check_in_one)
        
        self.log_widget = QListWidget()
        
        layout.addWidget(self.login_btn, 0, 2)
        layout.addWidget(lb1, 0, 0, Qt.AlignRight)
        layout.addWidget(self.nick_lb, 0, 1)
        layout.addWidget(lb2, 1, 0, Qt.AlignRight)
        layout.addWidget(self.check_sleep, 1, 1)
        layout.addWidget(self.super_topic_combo, 2, 0)
        layout.addWidget(self.refresh_btn, 2, 1)
        layout.addWidget(self.check_all_btn, 1, 2)
        layout.addWidget(self.check_one_btn, 2, 2)
        layout.addWidget(self.log_widget, 4, 0, 1, 3)
        self.setLayout(layout)
    
    def scan_qr(self):
        """
        开启线程，获取二维码信息
        :return:
        """
        self.session = requests.session()
        self.q_t = QRCodeThread(self.session)
        self.q_t.start()
        self.q_t.signal.connect(self.scan_login)
    
    def scan_login(self, qr_dict):
        """
        通过二维码，开启扫码窗口
        :param qr_dict:
        :return:
        """
        if not qr_dict:
            QMessageBox.warning(self, "警告", "获取二维码失败")
            return
        # 打开二维码
        self.log_widget.addItem("获取二维码成功！")
        self.log_widget.setCurrentRow(self.log_widget.count() - 1)
        self.scan_win = ScanImage(self.session, qr_dict)
        self.scan_win.show()
        self.scan_win.signal.connect(self._del_scan_login)
    
    def _del_scan_login(self, login_dict):
        """
        获取登录信息，处理登录结果
        :param login_dict:
        :return:
        """
        if login_dict['status']:
            self.cookie = login_dict['web_cookie']
            print(self.cookie)
            self.username = login_dict['user']['screen_name']
            self.nick_lb.setText(self.username)
            self.log_widget.addItem(f"{login_dict['user']['screen_name']}，{login_dict['msg']}")
            self.log_widget.setCurrentRow(self.log_widget.count() - 1)
            self.refresh_topic_list()
        else:
            self.log_widget.addItem(login_dict)
            self.log_widget.setCurrentRow(self.log_widget.count() - 1)
    
    def refresh_topic_list(self):
        if not self.cookie:
            QMessageBox.warning(self, "警告", "未检测到登录状态")
            return
        self.refresh_t = TopicListThread()
        self.refresh_t.cookie = self.cookie
        self.refresh_t.username = self.username
        self.refresh_t.start()
        self.refresh_t.signal.connect(self._del_refresh_topic_list)
        self.log_widget.addItem("正在获取超话列表。。。")
        self.log_widget.setCurrentRow(self.log_widget.count() - 1)
    
    def _del_refresh_topic_list(self, super_topic_list):
        if super_topic_list:
            self.super_topic_list = super_topic_list
            self.super_topic_combo.clear()
            for super_topic_dict in super_topic_list:
                print(super_topic_dict)
                self.super_topic_combo.addItem(super_topic_dict['title'])
            self.log_widget.addItem(f"获取超话列表成功，一共获取到超话数：{len(super_topic_list)}个")
            self.log_widget.setCurrentRow(self.log_widget.count() - 1)
        else:
            self.log_widget.addItem("获取超话列表失败")
            self.log_widget.setCurrentRow(self.log_widget.count() - 1)
    
    def check_in_all(self):
        if not self.cookie:
            QMessageBox.warning(self, "警告", "未检测到登录状态")
            return
        self.check_in_t = CheckIn(
            cookie=self.cookie, sleep_time=self.check_sleep.value(), topic_list=self.super_topic_list)
        self.check_in_t.start()
        self.check_in_t.signal.connect(self.push_msg)
    
    def check_in_one(self):
        if not self.cookie:
            QMessageBox.warning(self, "警告", "未检测到登录状态")
            return
        topic_name = self.super_topic_combo.currentText()
        super_topic = [i for i in self.super_topic_list if i['title'] == topic_name][0]
        result = super_topic_check_in(self.cookie, super_topic)
        self.log_widget.addItem(f"{topic_name}，{result['msg']}")
        self.log_widget.setCurrentRow(self.log_widget.count() - 1)
    
    def push_msg(self, msg):
        self.log_widget.addItem(msg)
        self.log_widget.setCurrentRow(self.log_widget.count() - 1)
    
    # 监听Dialog窗口右上角帮助按钮
    def event(self, event):
        if event.type() == QEvent.EnterWhatsThisMode:
            QWhatsThis.leaveWhatsThisMode()
            QDesktopServices.openUrl(QUrl("https://github.com/ReaJason"))
        return QDialog.event(self, event)
    
    # 窗口关闭按钮事件
    def closeEvent(self, event):
        reply = QMessageBox.question(self, '提醒', '确定要退出吗?', QMessageBox.Yes, QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()


def run():
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("myappid")
    
    QApplication.setStyle(QStyleFactory.create('Fusion'))
    
    app = QApplication(sys.argv)
    win = MainWin()
    win.show()
    sys.exit(app.exec_())
