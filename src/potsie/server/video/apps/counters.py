import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from potsie.core.xapi import make_distribution_for_verb

from ...config import external_stylesheets
from ..config import video_apps_pathname_prefix
from ..utils import get_metrics_for_video_id

app_pathname_prefix = f"{video_apps_pathname_prefix}/counters/"
app = dash.Dash(
    __name__,
    external_stylesheets=external_stylesheets,
    requests_pathname_prefix=app_pathname_prefix,
)
app.layout = html.Div(
    [
        dcc.Input(
            id="video-id",
            type="text",
            value="",
            placeholder="Video ID",
            # readOnly=True,
        ),
        dcc.Loading(
            id="loader",
            children=[dcc.Graph(id="video-verbs-calendar")],
            type="graph",
            fullscreen=True,
        ),
    ]
)


@app.callback(Output("video-verbs-calendar", "figure"), [Input("video-id", "value")])
def update_graph(video_id):

    if not video_id:
        return {}

    video_id = "79b5e3cc-2fe7-93ef-2c4e-2db9df883b18"
    metrics = get_metrics_for_video_id(video_id)

    played_dist = make_distribution_for_verb(metrics, "played")
    completed_dist = make_distribution_for_verb(metrics, "completed")
    initialized_dist = make_distribution_for_verb(metrics, "initialized")

    return {
        "data": [
            {
                "x": played_dist.index,
                "y": played_dist._id,
                "type": "line",
                "name": "played",
            },
            {
                "x": completed_dist.index,
                "y": completed_dist._id,
                "type": "line",
                "name": "completed",
            },
            {
                "x": initialized_dist.index,
                "y": initialized_dist._id,
                "type": "line",
                "name": "initialized",
            },
        ],
        "layout": {
            "title": "Unique statement per verb",
            "yaxis": {"title": "Occurrences"},
        },
    }
