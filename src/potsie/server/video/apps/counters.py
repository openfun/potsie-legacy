import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd

from potsie.core.factories import xAPIVideoMetricsFactory
from potsie.core.lrs import get_statements_for_id
from potsie.core.xapi import get_video_statements_metrics, select_metrics_for_verb
from ..config import video_apps_pathname_prefix
from ...config import external_stylesheets


def _get_metrics_for_video_id(video_id):
    """Query video statements to the LRS and convert statements to metrics"""
    return get_video_statements_metrics(get_statements_for_id(video_id))


def distribution(metrics, verb, group_by=pd.Grouper(freq="D"), unique=True):
    return (
        select_metrics_for_verb(metrics, verb, unique=unique)
        .groupby(by=group_by)
        .count()
    )


video_id = "126bd2fb-a846-cd73-2278-fedf9861560b"
# metrics = _get_metrics_for_video_id(video_id)
metrics = xAPIVideoMetricsFactory.build(
    count=30000,
    start_date="-1M",
    end_date="now",
    object_id=f"uuid://{video_id}",
    length=520,
)

initialized_dist = distribution(metrics, "initialized")
played_dist = distribution(metrics, "played")
completed_dist = distribution(metrics, "completed")

app_pathname_prefix = f"{video_apps_pathname_prefix}/counters/"
app = dash.Dash(
    __name__,
    external_stylesheets=external_stylesheets,
    requests_pathname_prefix=app_pathname_prefix,
)

app.layout = html.Div(
    children=[
        html.H1(children="Video analytics"),
        html.Div(children=f"ID: {video_id}"),
        html.Div(
            children=dcc.Graph(
                id="video-verbs-calendar",
                figure={
                    "data": [
                        {
                            "x": played_dist.index,
                            "y": played_dist.id,
                            "type": "line",
                            "name": "played",
                        },
                        {
                            "x": completed_dist.index,
                            "y": completed_dist.id,
                            "type": "line",
                            "name": "completed",
                        },
                        {
                            "x": initialized_dist.index,
                            "y": initialized_dist.id,
                            "type": "line",
                            "name": "initialized",
                        },
                    ],
                    "layout": {
                        "title": "Unique statement per verb",
                        "yaxis": {"title": "Occurrences"},
                    },
                },
            )
        ),
    ]
)
