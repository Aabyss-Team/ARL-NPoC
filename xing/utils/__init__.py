import subprocess
import shlex
import random
import string
import colorlog
import logging
import urllib3
import importlib
import os
import sys
from urllib.parse import urlparse
urllib3.disable_warnings()
import requests
import hashlib
from xing.utils.file import load_file,append_file
from xing.conf import Conf

def exec_system(cmd, **kwargs):
    logger = get_logger()

    cmd = " ".join(cmd)
    logger.debug("exec system : {}".format(cmd))
    timeout = 4 * 60 * 60

    stdout = subprocess.DEVNULL
    stderr = subprocess.DEVNULL

    if Conf.LOGGER_LEVEL <= logging.DEBUG:
        stdout = None
        stderr = None

    completed = subprocess.run(shlex.split(cmd), stdout=stdout,stderr=stderr, timeout=timeout, check=False, **kwargs)

    return completed


def random_choices(k = 6):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=k))




SUCCESS = Conf.SUCCESS_LEVEL
logging.addLevelName(SUCCESS, "SUCCESS")
def success(self, message, *args, **kws):
    if self.isEnabledFor(SUCCESS):
        self._log(SUCCESS, message, args, **kws) 
logging.Logger.success = success
 
def init_logger():
    log_colors = {
        'DEBUG': 'white',
        'INFO': 'green',
        'SUCCESS':  'red',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'bold_red',
    }

    handler = colorlog.StreamHandler()
    handler.setFormatter(colorlog.ColoredFormatter(
        fmt = '%(log_color)s[%(asctime)s] [%(levelname)s] '
              '[%(threadName)s] [%(filename)s:%(lineno)d] %(message)s', 
        log_colors = log_colors, datefmt = "%Y-%m-%d %H:%M:%S"))

    logger = colorlog.getLogger('xing')
    logger.setLevel(Conf.LOGGER_LEVEL)
    logger.addHandler(handler)
    logger.propagate = False


def get_celery_logger():
    try:
        from celery.utils.log import get_task_logger
        if 'celery' in sys.argv[0]:
            task_logger = get_task_logger(__name__)
            return task_logger
    except Exception as e:
        pass

    return None


def get_logger():
    task_logger = get_celery_logger()
    if task_logger is not None:
        return task_logger

    logger = logging.getLogger('xing')
    if not logger.handlers:
        init_logger()

    logger.setLevel(Conf.LOGGER_LEVEL)
    return logger


UA = "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36"


# http 请求封装函数
def http_req(url, method='get', **kwargs):
    if kwargs.get("disable_normal"):
        # 禁用 URL 规范化处理，仅仅支持GET
        return req_disable_normal(url)

    kwargs.setdefault('verify', False)
    kwargs.setdefault('timeout', (Conf.CONNECT_TIMEOUT, Conf.READ_TIMEOUT))
    kwargs.setdefault('allow_redirects', False)

    headers = kwargs.get("headers", {})
    if headers is None:
        headers = {}

    headers.setdefault("User-Agent", UA)

    random_ip = "10.0.{}.{}".format(random.randint(1, 254), random.randint(1, 254))
    headers.setdefault("X-Real-IP", random_ip)
    headers.setdefault("X-Forwarded-For", random_ip)

    kwargs["headers"] = headers

    proxies = {
        'https': Conf.PROXY_URL,
        'http': Conf.PROXY_URL
    }

    if Conf.PROXY_URL:
        kwargs["proxies"] = proxies

    conn = getattr(requests, method)(url, **kwargs)

    return conn


# 禁用规范化URL处理
def req_disable_normal(url):
    headers = {
        "User-Agent": UA
    }
    req = requests.Request(method='GET', url=url, headers=headers)
    prep = req.prepare()
    prep.url = url

    proxies = {}

    if Conf.PROXY_URL:
        proxies = {
            'http': Conf.PROXY_URL,
            'https': Conf.PROXY_URL
        }

    with requests.Session() as session:
        return session.send(prep, verify=False, proxies=proxies, timeout=(Conf.CONNECT_TIMEOUT, Conf.READ_TIMEOUT))


def md5(data):
    hash_md5 = hashlib.md5()
    hash_md5.update(data.encode(encoding='utf-8'))
    return hash_md5.hexdigest()


def content2text(context, encoding = "utf-8"):
    if isinstance(context, bytes):
        return context.decode(encoding, errors='ignore')

    return context


def parse_target_info(target):
    target = target.strip("/")

    if "://" not in target:
        target = "http://" + target

    parse = urlparse(target)
    
    port = parse.port

    if not parse.port:
        if parse.scheme == 'http':
            port = 80
        if parse.scheme == 'https':
            port = 443

    item = {
        'target':  target,
        'host': parse.hostname,
        'port': port,
        'scheme': parse.scheme
    }

    return item


from xing.utils.loader import load_all_plugin, load_plugins
from xing.utils.filter import pattern_match