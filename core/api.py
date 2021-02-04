"""
接口来自于：https://weibo.com/，新版界面
__author__ = "ReaJason"
__date__ = "2021年2月4日"
__site__ = "https://reajason.top"
__email__ = "reajason@163.com"
"""
from utils.requests_strength import pac_requests


# 获取用户id
def get_uid(cookie):
    res = pac_requests('GET', "https://weibo.com/ajax/side/userType", headers_={"cookie": cookie})
    if res['status']:
        return res['response'].headers.get('X-Log-Uid')
    return None


# 获取用户信息
def get_user_info(uid, cookie):
    res = pac_requests('GET', f"https://weibo.com/ajax/profile/info?uid={uid}", headers_={"cookie": cookie})
    if res['status']:
        return res['response'].json()['data']['user']
    return None