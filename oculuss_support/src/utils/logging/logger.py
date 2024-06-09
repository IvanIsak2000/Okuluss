from logtail import LogtailHandler
import logging

from utils.config import LOG_TOKEN
handler = LogtailHandler(source_token=LOG_TOKEN)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.handlers = []
logger.addHandler(handler)

logger.info("\n\n\n\n\nLogger initialized")
