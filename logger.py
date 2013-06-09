from libs.singleton import Singleton
import logging

@Singleton
class MyLogger(object):
    def __init__(self):
        self.logger = logging.getLogger('PlagiarismDetector')
        hdlr = logging.FileHandler('data/log.log')
        formatter = logging.Formatter('%(asctime)s %(message)s')
        hdlr.setFormatter(formatter)
        self.logger.addHandler(hdlr)
        self.logger.setLevel(logging.INFO)

    def info(self, message):
        self.logger.info(message)

Logger = MyLogger.Instance()