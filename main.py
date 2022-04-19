# encoding:utf-8
import logging

logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(levelname)s - %(message)s')

import ssl

ssl._create_default_https_context = ssl._create_unverified_context
import requests
import selenium
import platform
from sqlalchemy import create_engine

from selenium.webdriver import Chrome, ChromeOptions
from selenium.common.exceptions import TimeoutException
import os
from dotenv import load_dotenv
import difflib
import zipfile
from website import *


# 创建mysql引擎，用于数据入库
def createMysqlEngine(user, password, host, database, port=3306):
    engine = create_engine(f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}")
    return engine


# 获得Selenium对象
def getSelenium(chromeDriverPath, headless=False):
    options = ChromeOptions()
    if platform.system() == "Linux":
        options.add_argument('--headless')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument("--no-sandbox")
    else:
        options.headless = headless
    browser = Chrome(chromeDriverPath, options=options)
    return browser


# 压缩包解压
def uncompress(compressedFile):
    zip_file = zipfile.ZipFile(compressedFile)
    zip_list = zip_file.namelist()
    for f in zip_list:
        logging.info(f"[{f}]解压成功")
        zip_file.extract(f, os.path.join(os.getcwd(), "driver"))
    zip_file.close()


# 下载文件
def downloadFile(url, fileName):
    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36",
    }
    # 下载
    response = requests.get(url.strip(), stream=True, headers=headers)
    with(open(fileName, 'ab')) as f:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
    logging.info(f"[{fileName}]下载成功")
    return True


# 自动下载符合浏览器版本的驱动
def autoDownloadDriver(exceptionInfo):
    # 从异常信息中，获取当前浏览器版本
    localBrowserVersion = re.findall(r"Current browser version is (.*?) with", exceptionInfo)
    # 本地浏览器版本
    if localBrowserVersion:
        localDirverVersion = localBrowserVersion[0]
    logging.info(f"当前浏览器版本:{localDirverVersion}")
    # 获取所有驱动版本
    allVersion = requests.get("http://chromedriver.storage.googleapis.com/?delimiter=/&prefix=").text
    # 存储驱动版本 -> 驱动版本和本地浏览器版本的相似度
    tempkv = {}
    for i in re.findall(r"<Prefix>(.*?)</Prefix>", allVersion):
        similar = difflib.SequenceMatcher(None, localDirverVersion, i.strip()[:-1]).quick_ratio()
        tempkv[i] = similar
    # 按照相似度排序，取相似度最高的一个
    matchedDirverVersion = sorted(tempkv.items(), key=lambda i: i[1], reverse=True)[0][0]
    logging.info(f"即将下载驱动的版本:{matchedDirverVersion}")
    if platform.system() == "Linux":
        driverUrl = f"http://chromedriver.storage.googleapis.com/{matchedDirverVersion}chromedriver_linux64.zip"
    else:
        driverUrl = f"http://chromedriver.storage.googleapis.com/{matchedDirverVersion}chromedriver_win32.zip"
    # 下载文件
    downloadFile(driverUrl, r"driver/chromedriver_win32.zip")
    # 解压文件
    uncompress('driver/chromedriver_win32.zip')


# 初始化驱动，如果驱动版本和浏览器版本不符合，可以自动下载最匹配的驱动。
def initDriver(chromeDriverPath):
    try:
        slm = getSelenium(chromeDriverPath)
    # 驱动和浏览器版本不一致
    except selenium.common.exceptions.SessionNotCreatedException as e:
        logging.error("驱动和浏览器版本不一致，正在重新匹配版本。")
        autoDownloadDriver(str(e))
        return False
    return slm


if __name__ == '__main__':
    # 把配置文件读入环境变量
    env_path = os.path.join(os.getcwd(), '.env')
    load_dotenv(dotenv_path=env_path)
    # 驱动地址，目前只支持谷歌浏览器
    if platform.system() == "Linux":
        chromeDriverPath = r'driver/chromedriver'
    else:
        chromeDriverPath = r'driver/chromedriver.exe'
    # 构建mysql，便于数据入库
    engine = createMysqlEngine(os.environ["user138"], os.environ["pass138"], os.environ["url138"], os.environ["db138"])
    # 初始化驱动
    while 1:
        slm = initDriver(chromeDriverPath)
        if slm:
            break
    # 执行热事爬取
    for i in dir():
        if i.startswith("get") and i.endswith("TopNews"):
            try:
                exec(i + "(slm,engine)")
            except Exception as e:
                logging.error(f"{i}遇到的错误：{e}")
    # 关闭
    slm.close()
    slm.quit()
