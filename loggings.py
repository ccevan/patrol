import logging

# create logger
# logger_name = __name__
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
# 终端输出的级别

# create file handler
log_path = "./log.log"  # 文件存放位置
fh = logging.FileHandler(log_path)
fh.setLevel(logging.INFO)
# 日志级别

# create formatter
fmt = "%(asctime)-15s %(levelname)s %(filename)s %(lineno)d %(process)d %(message)s"
# datefmt = "%a %d %b %Y %H:%M:%S"
datefmt = "%Y-%m-%dT%H:%M:%S"

formatter = logging.Formatter(fmt, datefmt)

# add handler and formatter to logger
fh.setFormatter(formatter)
logger.addHandler(fh)
