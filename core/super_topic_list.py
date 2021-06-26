"""
获取超话列表
__author__ = "ReaJason"
__date__ = "2021年6月27日"
__site__ = "https://reajason.top"
__email__ = "reajason@163.com"
"""
import itertools
import time

from PyQt5.QtCore import QThread, pyqtSignal

from utils.requests_strength import pac_requests


def get_follow_topic_list_from_internet(cookie):
    url = 'https://weibo.com/ajax/profile/topicContent?tabid=231093_-_chaohua&page={}'
    super_topic_list = []
    for page_num in itertools.count(1):
        time.sleep(1)
        res = pac_requests('GET', url.format(page_num), headers_={"cookie": cookie})
        print(res['response'].json())
        if not res['status']:
            return []
        lists = res['response'].json()['data']['list']
        if not lists:
            return super_topic_list
        super_topic_list.extend(
            [
                {
                    'title': _['title'],
                    'id': _['oid'].split(':')[-1],
                    # 'url': f'https:{_["link"]}',
                    # 'pic': _['pic'].replace('thumbnail', 'large'),
                } for _ in lists
            ]
        )


class TopicListThread(QThread):
    signal = pyqtSignal(list)
    
    def __int__(self):
        super(TopicListThread, self).__int__()
        self.cookie = None
        self.username = None
    
    def run(self):
        super_topic_list = get_follow_topic_list_from_internet(self.cookie)
        self.signal.emit(super_topic_list)
