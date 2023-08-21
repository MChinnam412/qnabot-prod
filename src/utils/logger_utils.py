import logging
import sys

class Logger:
    logger = None
    def __init__(self):
        try:
            logging.basicConfig(level=logging.INFO, format="%(asctime)s :[%(levelname)s]: %(message)s")
            logging.StreamHandler(sys.stdout)
            self.logger = logging.getLogger(__name__)
        except Exception as ex:
            print("Error while initializing Logger")

    def get_logger(self):
        return self.logger