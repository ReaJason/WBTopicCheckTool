"""
扫码登陆
__author__ = "ReaJason"
__date__ = "2021年2月4日"
__site__ = "https://reajason.top"
__email__ = "reajason@163.com"
"""
import time
import re

from PyQt5.QtCore import QThread, pyqtSignal
from core.api import get_uid, get_user_info


def get_qrcode(session):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/86.0.4240.75 Safari/537.36"
    }
    qrcode_url = "https://login.sina.com.cn/sso/qrcode/image?entry=account&size=256&callback=1"
    try:
        session.get('https://m.weibo.cn/', headers=headers)
        res = session.get(qrcode_url, headers=headers)
        return {
            'img_url': re.findall(',"image":"(.*)"', res.text)[0].replace('\/', '/'),
            'qrid': re.findall('"qrid":"(.*?)"', res.text)[0]
        }
    except:
        return {}


class QRCodeThread(QThread):
    signal = pyqtSignal(dict)
    
    def __init__(self, session):
        super().__init__()
        self.session = session
    
    def run(self):
        qr_dict = get_qrcode(self.session)
        self.signal.emit(qr_dict)

def login(session, alt):
    login_url = "https://login.sina.com.cn/sso/login.php"
    login_params = {
        "entry": "weibo",
        "returntype": "TEXT",
        "crossdomain": "1",
        "cdult": "3",
        "domain": "weibo.com",
        "alt": alt,
        "savestate": "30",
        "callback": "1",
    }
    try:
        res = session.get(login_url, params=login_params, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/86.0.4240.75 Safari/537.36"
        })
        # print(re.findall('"(.*?)"', res.text)[-1].replace('\/', '/'))
        session.get(url=re.findall('"(.*?)"', res.text)[-1].replace('\/', '/'), headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/86.0.4240.75 Safari/537.36"
        })
    except :
        return {'status': 0, 'msg':  '网络出错/账号异常'}
    cookie = ''
    count = 0
    for k, v in session.cookies.items():
        if k == 'SUB' and count:
            cookie += f"{k}={v}; "
        if k == 'SUB':
            count += 1
    uid = get_uid(cookie)
    if uid:
        user_info = get_user_info(uid, cookie)
        return {'status': 1, 'user': user_info, 'web_cookie': cookie, 'msg': "登录成功"}
    else:
        return {'status': 0, 'msg': '网络出错/账号异常'}


class ScanPicThread(QThread):
    scan_signal = pyqtSignal(dict)
    
    def __init__(self, win, session, qrid):
        super(ScanPicThread, self).__init__()
        self.qrid = qrid
        self.win = win
        self.session = session
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/86.0.4240.75 Safari/537.36",
            "Referer": "http://my.sina.com.cn/"
        }
    
    def run(self):
        while True:
            # 扫码窗口关闭，则结束扫码检测
            if not self.win.isVisible():
                return
            check_url = f"https://login.sina.com.cn/sso/qrcode/check?entry=weibo&qrid={self.qrid}&callback=1"
            try:
                time.sleep(1)
                res = self.session.get(check_url, headers=self.headers)
                msg = re.findall(',"msg":"(.*?)"', res.text)[0]
                code = re.findall(':(\d{8})', res.text)[0]
                if code == '50114002':
                    pass
                    # print(msg)
                if code == '50114001':
                    pass
                    # print(msg)
                if code == '20000000':
                    alt = re.findall('"alt":"(.*?)"', res.text)[0]
                    login_dict = login(self.session, alt)
                    self.scan_signal.emit(login_dict)
            except Exception as e:
                print(e)
                print(e.__class__)