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

app_pathname_prefix = f"{video_apps_pathname_prefix}/events/"
app = dash.Dash(
    __name__,
    external_stylesheets=external_stylesheets,
    requests_pathname_prefix=app_pathname_prefix,
)
played_all = select_metrics_for_verb(metrics, "played", unique=False)
played_all_dist = distribution(
    played_all,
    "played",
    group_by=played_all["time"].apply(lambda x: round(x, 0)),
    unique=False,
)

paused_all = select_metrics_for_verb(metrics, "paused", unique=False)
paused_all_dist = distribution(
    paused_all,
    "paused",
    group_by=paused_all["time"].apply(lambda x: round(x, 0)),
    unique=False,
)

seeked_all = select_metrics_for_verb(metrics, "seeked", unique=False)
seeked_all_from_dist = distribution(
    seeked_all,
    "seeked",
    group_by=seeked_all["time_from"].apply(lambda x: round(x, 0)),
    unique=False,
)

seeked_all_to_dist = distribution(
    seeked_all,
    "seeked",
    group_by=seeked_all["time_to"].apply(lambda x: round(x, 0)),
    unique=False,
)

terminated_all = select_metrics_for_verb(metrics, "terminated", unique=False)
terminated_all_dist = distribution(
    terminated_all,
    "terminated",
    group_by=terminated_all["time"].apply(lambda x: round(x, 0)),
    unique=False,
)

app.layout = html.Div(
    children=[
        html.H1(children="Video events"),
        html.Div(children=f"ID: {video_id}"),
        html.Div(
            children=dcc.Graph(
                id="video-events",
                figure={
                    "data": [
                        {
                            "x": played_all_dist.index,
                            "y": played_all_dist.id,
                            "type": "line",
                            "name": "played",
                        },
                        {
                            "x": paused_all_dist.index,
                            "y": paused_all_dist.id,
                            "type": "line",
                            "name": "paused",
                        },
                        {
                            "x": seeked_all_from_dist.index,
                            "y": seeked_all_from_dist.id,
                            "type": "line",
                            "name": "seeked (from)",
                        },
                        {
                            "x": seeked_all_to_dist.index,
                            "y": seeked_all_to_dist.id,
                            "type": "line",
                            "name": "seeked (to)",
                        },
                        {
                            "x": terminated_all_dist.index,
                            "y": terminated_all_dist.id,
                            "type": "line",
                            "name": "terminated",
                        },
                    ],
                    "layout": {
                        "title": "Video events",
                        "xaxis": {"title": "Video timecode (seconds)"},
                        "yaxis": {"title": "Occurrences"},
                    },
                },
            )
        ),
    ]
)
