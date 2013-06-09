from libs.singleton import Singleton
import logging
import os

log_dir = 'data/log.log'

@Singleton
class MyLogger(object):
    def __init__(self):
        if not os.path.exists(log_dir):
            os.mkdir(log_dir)

        self.logger = logging.getLogger('PlagiarismDetector')
        hdlr = logging.FileHandler(log_dir)
        formatter = logging.Formatter('%(asctime)s %(message)s')
        hdlr.setFormatter(formatter)
        self.logger.addHandler(hdlr)
        self.logger.setLevel(logging.INFO)

    def info(self, message):
        self.logger.info(message)

Logger = MyLogger.Instance()