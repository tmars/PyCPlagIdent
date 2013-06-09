from libs.singleton import Singleton
import logging
import os

log_path = 'data/log.log'

@Singleton
class MyLogger(object):
    def __init__(self):
        if not os.path.exists(log_path):
            open(log_path, 'w+').close()


        self.logger = logging.getLogger('PlagiarismDetector')
        hdlr = logging.FileHandler(log_path)
        formatter = logging.Formatter('%(asctime)s %(message)s')
        hdlr.setFormatter(formatter)
        self.logger.addHandler(hdlr)
        self.logger.setLevel(logging.INFO)

    def info(self, message):
        self.logger.info(message)

Logger = MyLogger.Instance()