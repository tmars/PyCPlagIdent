import logging
import os

class Logger(object):
    def __init__(self, filename):
        if not os.path.exists(filename):
            open(filename, 'w+').close()

        self.logger = logging.getLogger('PlagiarismDetector')
        hdlr = logging.FileHandler(filename)
        formatter = logging.Formatter('%(asctime)s %(message)s')
        hdlr.setFormatter(formatter)
        self.logger.addHandler(hdlr)
        self.logger.setLevel(logging.INFO)

    def info(self, message):
        self.logger.info(message)
