import logging
import os
import sys
import time
from logging.handlers import TimedRotatingFileHandler
# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# sys.path.append(BASE_DIR)

def create_logger():
    """创建日志"""
    log_file_name = 'logger-' + time.strftime('%Y-%m-%d', time.localtime(time.time())) + '.log'
    #log_file_str = '/home/runone/radar/radar_data/log'
    log_file_str = './log'
    logging_file_max_bytes = 300 * 1024 * 1024
    logging_file_backup = 10
    logging_info = 'INFO'
    logging_error = 'ERROR'

    # 设置info日志
    log_info = logging.getLogger('info.log')
    info_handler = logging.handlers.RotatingFileHandler(
        filename=log_file_str + '/infos' + os.sep +  log_file_name,
        maxBytes=logging_file_max_bytes,
        backupCount=logging_file_backup
    )
    logging_format = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(lineno)s - %(message)s')
    info_handler.setFormatter(logging_format)
    log_info.addHandler(info_handler)
    log_info.setLevel(logging_info)

    # 设置error日志
    log_info = logging.getLogger('error.log')
    error_handler = logging.handlers.RotatingFileHandler(
        filename=log_file_str + '/errors' + os.sep +  log_file_name,
        maxBytes=logging_file_max_bytes,
        backupCount=logging_file_backup
    )
    logging_format = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(lineno)s - %(message)s')
    error_handler.setFormatter(logging_format)
    log_info.addHandler(error_handler)
    log_info.setLevel(logging_error)


