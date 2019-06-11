from werkzeug.wsgi import DispatcherMiddleware

from .app import app as main_app
from .video.apps.counters import (
    app as video_counters,
    app_pathname_prefix as video_counters_pathname_prefix,
)
from .video.apps.events import (
    app as video_events,
    app_pathname_prefix as video_events_pathname_prefix,
)

# FIXME: this does not enable hot reload
if main_app.debug:
    video_counters.enable_dev_tools(debug=True)
    video_events.enable_dev_tools(debug=True)


app = DispatcherMiddleware(
    main_app,
    # Remove the trailing slash from Dash application path name prefix to avoid
    # infinite redirection loop within the middleware
    {
        video_counters_pathname_prefix.rstrip("/"): video_counters.server,
        video_events_pathname_prefix.rstrip("/"): video_events.server,
    },
)
