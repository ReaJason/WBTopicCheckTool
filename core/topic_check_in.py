"""
超话签到
__author__ = "ReaJason"
__date__ = "2021年2月4日"
__site__ = "https://reajason.top"
__email__ = "reajason@163.com"
"""
import time

from PyQt5.QtCore import QThread, pyqtSignal
from utils.requests_strength import pac_requests, get_user_agent


def super_topic_check_in(cookie, super_topic_dict):
    url = 'https://weibo.com/p/aj/general/button'
    params = {
        "ajwvr": "6",
        "api": "http://i.huati.weibo.com/aj/super/checkin",
        "texta": "签到",
        "textb": "已签到",
        "status": "0",
        "id": super_topic_dict["id"],
        "location": "page_100808_super_index",
        "timezone": "GMT 0800",
        "lang": "zh-cn",
        "plat": "Win32",
        "ua": get_user_agent,
        "screen": "1536*864",
        "__rnd": str(int(round(time.time() * 1000))),
    }
    res = pac_requests('GET', url, params=params, headers_={'cookie': cookie,
                                                            'referer': f'https://weibo.com/p/{super_topic_dict["id"]}/super_index'})
    print(res)
    if not res['status']:
        return {'status': 0, 'msg': res['errmsg']}
    try:
        print(res['response'].text)
        res['response'].json()
    except:
        return {'status': 0, 'msg': "请求异常"}
    if res['response'].json()['code'] == '100000':
        return {
            'status': 1,
            'msg': f'{res["response"].json()["data"]["alert_title"]}，{res["response"].json()["data"]["alert_subtitle"]}'
        }
    elif res['response'].json()['code'] == 382004:
        return {'status': 1, 'msg': '今天已签到'}
    elif res['response'].json()['code'] == 382003:
        return {'status': 0, 'msg': '请先关注再签到'}
    else:
        return {'status': 0, 'msg': res['response'].json()['msg']}


class CheckIn(QThread):
    signal = pyqtSignal(str)

    def __init__(self, sleep_time, topic_list, cookie):
        super(CheckIn, self).__init__()
        self.sleep_time = sleep_time
        self.topic_list = topic_list
        self.cookie = cookie

    def run(self):
        for index, topic_dict in enumerate(self.topic_list):
            time.sleep(self.sleep_time)
            result = super_topic_check_in(cookie=self.cookie, super_topic_dict=topic_dict)
            self.signal.emit(f"{index + 1}:{topic_dict['title']}，{result['msg']}")
        self.signal.emit("所有超话签到完毕，如有失败请单签")
