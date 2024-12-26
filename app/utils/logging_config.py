import logging
import sys

from app.utils.constants import IS_LOCAL

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# add formatter to ch
if IS_LOCAL:
    ch = logging.FileHandler(filename = 'error.log')
    ch.setFormatter(formatter)

else:
    ch = logging.StreamHandler(stream = sys.stdout)
    ch.setFormatter(formatter)

logger.addHandler(ch)