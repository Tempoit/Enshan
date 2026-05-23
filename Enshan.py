import requests, json, time, os, sys
sys.path.append('.')
requests.packages.urllib3.disable_warnings()
from lxml import etree

cookie = os.environ.get("cookie_enshan")

def get_formhash(s, cookie_val):
    """获取 formhash"""
    url = "https://www.right.com.cn/forum/forum.php"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
        'Cookie': cookie_val,
        'Referer': 'https://www.right.com.cn/forum/'
    }
    try:
        r = s.get(url, headers=headers, timeout=30)
        h = etree.HTML(r.text)
        formhash = h.xpath('//input[@name="formhash"]/@value')
        if formhash:
            return formhash[0]
    except:
        pass
    return None

def run(cookie_val):
    msg = ""
    s = requests.Session()
    s.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0'
    })

    # Step 1: 获取 formhash
    formhash = get_formhash(s, cookie_val)
    if not formhash:
        return '签到失败: 无法获取 formhash，可能是 cookie 失效了！'

    # Step 2: 调用签到 API
    sign_url = "https://www.right.com.cn/forum/plugin.php?id=erling_qd:action&action=sign"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'X-Requested-With': 'XMLHttpRequest',
        'Origin': 'https://www.right.com.cn',
        'Referer': 'https://www.right.com.cn/forum/plugin.php?id=erling_qd-sign_in',
        'Cookie': cookie_val
    }
    data = f'formhash={formhash}'

    try:
        r = s.post(sign_url, headers=headers, data=data, timeout=30)
        if r.status_code == 200:
            try:
                result = r.json()
                if result.get('success'):
                    credit = result.get('credit', '?')
                    days = result.get('continuous_days', '?')
                    message = result.get('message', '签到成功')
                    msg += f'签到成功! {message}，获得积分: {credit}，连续签到: {days} 天'
                else:
                    msg += f'签到失败: {result.get("message", "未知错误")}'
            except:
                # 可能是已经签到过了
                if '已经' in r.text or '今日' in r.text:
                    msg += '今日已签到'
                else:
                    msg += f'签到失败: 服务器返回 {r.status_code}'
        else:
            msg += f'签到失败: HTTP {r.status_code}'
    except requests.exceptions.Timeout:
        msg = '签到失败: 请求超时，请检查网络连接'
    except Exception as e:
        msg = f'签到失败: 无法连接到网站 ({str(e)[:100]})'

    return msg + '\n'

def main():
    msg = ""
    global cookie
    if "\\n" in cookie:
        clist = cookie.split("\\n")
    elif "\n" in cookie:
        clist = cookie.split("\n")
    else:
        clist = [cookie]

    i = 0
    while i < len(clist):
        msg += f"第 {i+1} 个账号开始执行任务\n"
        msg += run(clist[i])
        i += 1
    print(msg[:-1])
    return msg[:-1]


if __name__ == "__main__":
    if cookie:
        print("----------恩山论坛开始尝试签到----------")
        print('当前北京时间为:' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time() + 28800)))
        main()
        print("----------恩山论坛签到执行完毕----------")
    else:
        print("错误: 未设置 cookie_enshan 环境变量")
