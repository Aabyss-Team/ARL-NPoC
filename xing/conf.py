import os
import logging
import tempfile

class Conf(object):
    """运行配置类"""

    """源码目录"""
    PROJECT_DIRECTORY = os.path.abspath(os.path.dirname(__file__))

    """系统插件目录"""
    SYSTEM_PLUGINS_DIR = os.path.join(PROJECT_DIRECTORY, "plugins")

    """用户自定义目录"""
    USER_PLUGINS_DIR = None

    """代理地址"""
    PROXY_URL = None

    """TXT格式保存文件名"""
    SAVE_TEXT_RESULT_FILENAME = "npoc_result_txt.txt"

    """JSON格式保存文件名"""
    SAVE_JSON_RESULT_FILENAME = "npoc_result_json.txt"

    DUMP_RESULT_REQ_FLAG = False

    """连接超时时间"""
    CONNECT_TIMEOUT = 5.1
    """读取超时时间"""
    READ_TIMEOUT = 10.1

    """日志等级"""
    LOGGER_LEVEL = logging.INFO

    SUCCESS_LEVEL = 51

    """临时目录"""
    TEMP_DIR = tempfile.gettempdir()



