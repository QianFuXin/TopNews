# encoding:utf-8
import ssl

ssl._create_default_https_context = ssl._create_unverified_context
from bs4 import BeautifulSoup
import re
import pandas as pd
import time
from selenium.common.exceptions import TimeoutException


# 百度热事
def getBaiduTopNews(slm, engine):
    url = "https://top.baidu.com/board?tab=realtime"
    slm.set_page_load_timeout(20)
    slm.set_script_timeout(20)
    try:
        slm.get(url)
        time.sleep(10)
    except TimeoutException:
        slm.execute_script('window.stop()')
    finally:
        html = slm.page_source
        parsed = BeautifulSoup(html, "html.parser")
    allUrl = []
    allTitle = []
    allHotNumber = []
    timeNow = time.strftime("%Y%m%d %H:%M", time.localtime())
    """"""
    for i in parsed.find_all(class_=re.compile("^category-wrap.*")):
        data = i.find(class_=re.compile('^content.*'))
        url = data.find('a').get('href').strip()
        title = data.find('a').find('div').text.strip()
        hotNumber = i.find(class_=re.compile('^trend.*')).find(class_=re.compile('^hot.*')).text.strip()
        allUrl.append(url)
        allTitle.append(title)
        allHotNumber.append(hotNumber)
    df = pd.DataFrame({'title': allTitle,
                       'url': allUrl,
                       'hotNumber': allHotNumber})
    df["timeNow"] = timeNow
    df.to_sql("baiDuTopNews", engine, if_exists="append", index=False)


# 百度贴吧热事
def getBaiDuTieBaTopNews(slm, engine):
    url = "https://tieba.baidu.com/hottopic/browse/topicList?res_type=1"
    # 设置超时时间
    slm.set_page_load_timeout(20)
    slm.set_script_timeout(20)
    try:
        slm.get(url)
        time.sleep(10)
    except TimeoutException:
        slm.execute_script('window.stop()')
    finally:
        html = slm.page_source
        parsed = BeautifulSoup(html, "html.parser")
    allUrl = []
    allTitle = []
    allHotNumber = []
    timeNow = time.strftime("%Y%m%d %H:%M", time.localtime())
    for i in parsed.find(class_="topic-top-list").find_all("li"):
        url = i.find('a').get('href').strip()
        title = i.find('a').text.strip()
        hotNumber = i.find('span', class_="topic-num").text.strip()
        allUrl.append(url)
        allTitle.append(title)
        allHotNumber.append(hotNumber)
    df = pd.DataFrame({'title': allTitle,
                       'url': allUrl,
                       'hotNumber': allHotNumber})
    df["timeNow"] = timeNow
    df.to_sql("baiDuTieBaTopNews", engine, if_exists="append", index=False)


# 微博热事
def getWeiBoTopNews(slm, engine):
    url = "https://s.weibo.com/top/summary?cate=realtimehot"
    # 设置超时时间
    slm.set_page_load_timeout(20)
    slm.set_script_timeout(20)
    try:
        slm.get(url)
        time.sleep(10)
    except TimeoutException:
        slm.execute_script('window.stop()')
    finally:
        html = slm.page_source
        parsed = BeautifulSoup(html, "html.parser")
    allUrl = []
    allTitle = []
    allHotNumber = []
    timeNow = time.strftime("%Y%m%d %H:%M", time.localtime())
    """"""
    for i in parsed.find_all("td", class_="td-02"):
        title = i.find('a').text.strip()
        url = "https://s.weibo.com/" + i.find('a').get('href').strip()
        if i.find('span'):
            hotNumber = i.find('span').text.strip()
            hotNumber = re.sub("\D", "", hotNumber)
        else:
            hotNumber = 0
        allUrl.append(url)
        allTitle.append(title)
        allHotNumber.append(hotNumber)
    df = pd.DataFrame({'title': allTitle,
                       'url': allUrl,
                       'hotNumber': allHotNumber})
    df["timeNow"] = timeNow
    df.to_sql("weiBoTopNews", engine, if_exists="append", index=False)


# 知乎热事
def getZhihuTopNews(slm, engine):
    url = "https://www.zhihu.com/billboard"
    # 设置超时时间
    slm.set_page_load_timeout(20)
    slm.set_script_timeout(20)
    try:
        slm.get(url)
        time.sleep(10)
    except TimeoutException:
        slm.execute_script('window.stop()')
    finally:
        html = slm.page_source
        parsed = BeautifulSoup(html, "html.parser")
    allUrl = []
    allTitle = []
    allHotNumber = []
    timeNow = time.strftime("%Y%m%d %H:%M", time.localtime())
    """"""
    script_text = parsed.find("script", id="js-initialData")
    result = re.findall(r'"hotList":(.*),"guestFeeds"', str(script_text))
    temp = result[0].replace("false", "False").replace("true", "True")
    hot_list = eval(temp)

    for i in hot_list:
        title = i["target"]["titleArea"]["text"].strip()
        hotNumberTemp = i["target"]["metricsArea"]["text"].strip()
        hotNumber = re.sub("\s", "", hotNumberTemp).replace("热度", "")
        url = i["target"]["link"]["url"].strip()
        allUrl.append(url)
        allTitle.append(title)
        allHotNumber.append(hotNumber)
    df = pd.DataFrame({'title': allTitle,
                       'url': allUrl,
                       'hotNumber': allHotNumber})
    df["timeNow"] = timeNow
    df.to_sql("zhiHuTopNews", engine, if_exists="append", index=False)


# B站热事
def getBiliTopNews(slm, engine):
    url = "https://www.bilibili.com/v/popular/rank/all"
    # 设置超时时间
    slm.set_page_load_timeout(20)
    slm.set_script_timeout(20)
    try:
        slm.get(url)
        time.sleep(10)
    except TimeoutException:
        slm.execute_script('window.stop()')
    finally:
        html = slm.page_source
        parsed = BeautifulSoup(html, "html.parser")
    allUrl = []
    allTitle = []
    allHotNumber = []
    timeNow = time.strftime("%Y%m%d %H:%M", time.localtime())
    for i in parsed.find('ul', class_="rank-list").find_all('li'):
        data = i.find('div', class_="info")
        url = data.find('a').get('href').strip()[2:]
        title = data.find('a').text.strip()
        hotNumber = data.find('div', class_="detail-state").find('span', class_='data-box').text.strip()
        allUrl.append(url)
        allTitle.append(title)
        allHotNumber.append(hotNumber)
    df = pd.DataFrame({'title': allTitle,
                       'url': allUrl,
                       'hotNumber': allHotNumber})
    df["timeNow"] = timeNow
    df.to_sql("biLiTopNews", engine, if_exists="append", index=False)


# 抖音热事
def getDouYinTopNews(slm, engine):
    url = "https://www.douyin.com/hot"
    # 设置超时时间
    slm.set_page_load_timeout(20)
    slm.set_script_timeout(20)
    try:
        slm.get(url)
        time.sleep(10)
    except TimeoutException:
        slm.execute_script('window.stop()')
    finally:
        # 关闭登录提示框
        closeLoginPage = slm.find_element_by_class_name("dy-account-close")
        if closeLoginPage:
            closeLoginPage.click()
        time.sleep(2)
        html = slm.page_source
        parsed = BeautifulSoup(html, "html.parser")
    allUrl = []
    allTitle = []
    allHotNumber = []
    timeNow = time.strftime("%Y%m%d %H:%M", time.localtime())
    for i in parsed.find_all(text="抖音热榜"):
        for brotherTags in i.parent.next_siblings:
            if brotherTags.find_all('li'):
                for li in brotherTags.find_all('li'):
                    url = li.find('a').get('href').strip()
                    title = li.find('a').text.strip()
                    if li.find('span'):
                        hotNumber = li.find('span').text.strip()
                    else:
                        hotNumber = "0"
                    allUrl.append(url)
                    allTitle.append(title)
                    allHotNumber.append(hotNumber)
                break
            else:
                continue
    df = pd.DataFrame({'title': allTitle,
                       'url': allUrl,
                       'hotNumber': allHotNumber})
    df["timeNow"] = timeNow
    df.to_sql("douYinTopNews", engine, if_exists="append", index=False)
