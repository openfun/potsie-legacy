import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd

from potsie.core.factories import xAPIVideoMetricsFactory
from potsie.core.xapi import make_distribution_for_verb, select_metrics_for_verb
from ...config import external_stylesheets
from ..config import video_apps_pathname_prefix
from ..utils import get_metrics_for_video_id


app_pathname_prefix = f"{video_apps_pathname_prefix}/events/"
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
            children=[dcc.Graph(id="video-events")],
            type="graph",
            fullscreen=True,
        ),
    ]
)


@app.callback(Output("video-events", "figure"), [Input("video-id", "value")])
def update_graph(video_id):

    if not video_id:
        return {}

    metrics = get_metrics_for_video_id(video_id)
    played_all = select_metrics_for_verb(metrics, "played", unique=False)
    played_all_dist = make_distribution_for_verb(
        played_all,
        "played",
        group_by=played_all["time"].apply(lambda x: round(x, 0)),
        unique=False,
    )

    paused_all = select_metrics_for_verb(metrics, "paused", unique=False)
    paused_all_dist = make_distribution_for_verb(
        paused_all,
        "paused",
        group_by=paused_all["time"].apply(lambda x: round(x, 0)),
        unique=False,
    )

    seeked_all = select_metrics_for_verb(metrics, "seeked", unique=False)
    seeked_all_from_dist = make_distribution_for_verb(
        seeked_all,
        "seeked",
        group_by=seeked_all["time_from"].apply(lambda x: round(x, 0)),
        unique=False,
    )

    seeked_all_to_dist = make_distribution_for_verb(
        seeked_all,
        "seeked",
        group_by=seeked_all["time_to"].apply(lambda x: round(x, 0)),
        unique=False,
    )

    terminated_all = select_metrics_for_verb(metrics, "terminated", unique=False)
    terminated_all_dist = make_distribution_for_verb(
        terminated_all,
        "terminated",
        group_by=terminated_all["time"].apply(lambda x: round(x, 0)),
        unique=False,
    )

    return {
        "data": [
            {
                "x": played_all_dist.index,
                "y": played_all_dist._id,
                "type": "line",
                "name": "played",
            },
            {
                "x": paused_all_dist.index,
                "y": paused_all_dist._id,
                "type": "line",
                "name": "paused",
            },
            {
                "x": seeked_all_from_dist.index,
                "y": seeked_all_from_dist._id,
                "type": "line",
                "name": "seeked (from)",
            },
            {
                "x": seeked_all_to_dist.index,
                "y": seeked_all_to_dist._id,
                "type": "line",
                "name": "seeked (to)",
            },
            {
                "x": terminated_all_dist.index,
                "y": terminated_all_dist._id,
                "type": "line",
                "name": "terminated",
            },
        ],
        "layout": {
            "title": f"Events for video {video_id}",
            "xaxis": {"title": "Timecode (seconds)"},
            "yaxis": {"title": "Occurrences"},
        },
    }
