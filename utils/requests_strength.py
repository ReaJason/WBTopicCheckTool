import requests
import random


def get_user_agent():
    windows_user_agent = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 '
        'Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 '
        'Safari/537.36 Edg/86.0.622.68',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:80.0) Gecko/20100101 Firefox/80.0'
    ]
    return random.choice(windows_user_agent)


def pac_requests(method, url, timeout=30, headers_=None, **kwargs):
    headers = {
        'user-agent': get_user_agent()
    }
    if headers_:
        headers.update(headers_)
    try:
        res = requests.request(
            method=method,
            url=url,
            timeout=timeout, headers=headers, **kwargs)
        if res.status_code == 200:
            return {'status': 1, 'response': res}
        else:
            print(f'访问出错，{res.status_code}')
            print(res.text)
            return {'status': 0, 'errmsg': f'访问出错，{res.status_code}'}
    except requests.exceptions.ConnectionError:
        print('无法访问网络，获取失败')
        return {'status': 0, 'errmsg': '无法访问网络，获取失败'}
    except requests.exceptions.ConnectTimeout:
        print('网络连接超时，获取失败')
        return {'status': 0, 'errmsg': '网络连接超时，获取失败'}
    except Exception as e:
        print(f'错误类型：{e}\n错误详情：{e.__class__}')
        return {'status': 0, 'errmsg': f'错误类型：{e}\n错误详情：{e.__class__}'}