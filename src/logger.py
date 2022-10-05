import logging


def create_logger(name):
    _logger = logging.getLogger(name=name)
    _logger.setLevel(level=logging.INFO)

    handler = logging.StreamHandler()
    handler.setLevel(level=logging.INFO)

    _logger.handlers = [handler]

    return _logger
