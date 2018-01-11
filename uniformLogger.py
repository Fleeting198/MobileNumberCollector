import logging.config

logging.config.fileConfig("logger.conf")
logger = logging.getLogger("default")