import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logger(name, log_file, level=logging.INFO):
    """Function to setup as many loggers as you want"""

    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')

    handler = RotatingFileHandler(log_file, maxBytes=2000000, backupCount=5)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger

# 确保日志目录存在
if not os.path.exists('logs'):
    os.makedirs('logs')

# 创建主应用日志记录器
main_logger = setup_logger('main_logger', 'logs/main.log')

# 创建数据库操作日志记录器
db_logger = setup_logger('db_logger', 'logs/database.log')

# 创建认证日志记录器
auth_logger = setup_logger('auth_logger', 'logs/auth.log')