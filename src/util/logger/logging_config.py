import logging


def setup_logger_config():
    formatter = '%(filename)s -- %(funcName)s() -- %(levelname)s -- %(message)s'
    logging.basicConfig(format=formatter, level=logging.DEBUG)
    logging.info('logger was set up')
