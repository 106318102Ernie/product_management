import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("uvicorn")
handlers = logging.StreamHandler()
handlers.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handlers.setFormatter(formatter)
logger.addHandler(handlers)
