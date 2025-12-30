import logging

logger = logging.getLogger("aurora_proto")
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
logger.setLevel(logging.INFO)
logger.addHandler(handler)


def info(msg: str, **kwargs):
    logger.info(msg + " " + str(kwargs))
