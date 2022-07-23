import logging

formatter = logging.Formatter(
    (
        "[%(levelname)s  %(name)s - %(module)s.py:%(lineno)s "
        "- %(funcName)s() - %(asctime)s] %(message)s"
    )
)
log_level = "INFO"
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
stream_handler.setLevel(log_level)

logger = logging.getLogger("jh-server")
logger.addHandler(stream_handler)
logger.setLevel(log_level)
logger.info(f"Log level set to {log_level}")
