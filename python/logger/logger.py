import logging

logging.basicConfig(format='%(levelname)s| %(filename)s:%(lineno)s %(message)s')
# Create logger
logger = logging.getLogger('File:Line# Debugger')
logger.setLevel(logging.DEBUG)

