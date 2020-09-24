import logging

from werkzeug.serving import run_simple

from .wsgi import app

logger = logging.getLogger()

# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(
    logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
)
logger.addHandler(ch)

run_simple("0.0.0.0", 8050, app, use_reloader=True, use_debugger=True)
