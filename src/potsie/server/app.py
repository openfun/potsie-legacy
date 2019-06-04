import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd

from potsie.core.factories import xAPIVideoMetricsFactory
from potsie.core.lrs import get_statements_for_id
from potsie.core.xapi import get_video_statements_metrics, select_metrics_for_verb

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

video_id = "126bd2fb-a846-cd73-2278-fedf9861560b"
# statements = get_statements_for_id(video_id)
# metrics = get_video_statements_metrics(statements)
metrics = xAPIVideoMetricsFactory.build(
    count=30000,
    start_date="-1M",
    end_date="now",
    object_id=f"uuid://{video_id}",
    length=520,
)


def distribution(metrics, verb, group_by=pd.Grouper(freq="D"), unique=True):
    return (
        select_metrics_for_verb(metrics, verb, unique=unique)
        .groupby(by=group_by)
        .count()
    )


initialized_dist = distribution(metrics, "initialized")
played_dist = distribution(metrics, "played")
completed_dist = distribution(metrics, "completed")

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
        html.H1(children="Video analytics"),
        html.Div(children=f"ID: {video_id}"),
        html.Div(
            className="row",
            children=[
                html.Div(
                    className="six columns",
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
                    ),
                ),
                html.Div(
                    className="six columns",
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
                    ),
                ),
            ],
        ),
    ]
)

if __name__ == "__main__":
    app.run_server(host="0.0.0.0", debug=True)
