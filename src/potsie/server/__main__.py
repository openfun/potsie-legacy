from werkzeug.serving import run_simple

from .wsgi import app


run_simple("0.0.0.0", 8050, app, use_reloader=True, use_debugger=True)
