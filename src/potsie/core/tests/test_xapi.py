import json
from datetime import datetime

import pandas as pd
from pandas.core.dtypes.dtypes import DatetimeTZDtype

from ..factories import xAPIVideoMetricsFactory
from ..xapi import (
    get_video_statements_metrics,
    select_metrics_for_verb,
    XAPI_VIDEO_VERB_COMPLETED,
    XAPI_VIDEO_VERB_INITIALIZED,
    XAPI_VIDEO_VERB_INTERACTED,
    XAPI_VIDEO_VERB_PAUSED,
    XAPI_VIDEO_VERB_PLAYED,
    XAPI_VIDEO_VERB_SEEKED,
    XAPI_VIDEO_VERB_TERMINATED,
)
from . import FIXTURES_RECORDS_COLLECTION_PATH


def test_get_video_statements_metrics():
    """Test get_video_statements_metrics."""

    with open(FIXTURES_RECORDS_COLLECTION_PATH) as fixture:
        metrics = get_video_statements_metrics(json.load(fixture))

    assert len(metrics) == 7
    assert type(metrics.index.dtype) == DatetimeTZDtype

    selected = metrics[(metrics._id == "e21e30b7-4093-40b7-9808-e2f7a3994bb7")]
    assert selected.index[0] == pd.to_datetime("2019-06-14T09:06:37.504000+00:00")

    metric = selected.iloc[0]
    assert metric._id == "e21e30b7-4093-40b7-9808-e2f7a3994bb7"
    assert metric.verb == XAPI_VIDEO_VERB_COMPLETED
    assert metric.actor == "8a843c9aaf1f125b85854d555f7cfacc"
    assert metric.object_id == "uuid://e73a3ac1-b71e-4a0c-ae96-15400565d3ce"
    assert metric.length == 348.717
    assert metric.speed == 1.0
    assert metric.time == 348.748
    assert pd.isna(metric.time_from)
    assert pd.isna(metric.time_to)

    # Test ordering (by timestamp)
    assert metrics.index[0] < metrics.index[1]
    assert metrics.index[1] < metrics.index[2]
    assert metrics.index[2] < metrics.index[3]
    assert metrics.index[3] < metrics.index[4]
    assert metrics.index[4] < metrics.index[5]
    assert metrics.index[5] < metrics.index[6]
    assert metrics.iloc[0].verb == XAPI_VIDEO_VERB_SEEKED
    assert metrics.iloc[1].verb == XAPI_VIDEO_VERB_PLAYED
    assert metrics.iloc[2].verb == XAPI_VIDEO_VERB_PAUSED
    assert metrics.iloc[3].verb == XAPI_VIDEO_VERB_INTERACTED
    assert metrics.iloc[4].verb == XAPI_VIDEO_VERB_TERMINATED
    assert metrics.iloc[5].verb == XAPI_VIDEO_VERB_INITIALIZED
    assert metrics.iloc[6].verb == XAPI_VIDEO_VERB_COMPLETED

    # Completed
    selected = metrics[(metrics.verb == XAPI_VIDEO_VERB_COMPLETED)]
    assert len(selected) == 1
    assert selected.iloc[0].length == 348.717
    assert selected.iloc[0].time == 348.748

    # Initialized
    selected = metrics[(metrics.verb == XAPI_VIDEO_VERB_INITIALIZED)]
    assert len(selected) == 1
    assert selected.iloc[0].length == 136.81
    assert selected.iloc[0].speed == 1.5

    # Interacted
    selected = metrics[(metrics.verb == XAPI_VIDEO_VERB_INTERACTED)]
    assert len(selected) == 1
    assert selected.iloc[0].speed == 1.0
    assert pd.isna(selected.iloc[0].time)

    # Paused
    selected = metrics[(metrics.verb == XAPI_VIDEO_VERB_PAUSED)]
    assert len(selected) == 1
    assert selected.iloc[0].length == 291.108
    assert selected.iloc[0].time == 152.268

    # Played
    selected = metrics[(metrics.verb == XAPI_VIDEO_VERB_PLAYED)]
    assert len(selected) == 1
    assert selected.iloc[0].time == 148.774

    # Seeked
    selected = metrics[(metrics.verb == XAPI_VIDEO_VERB_SEEKED)]
    assert len(selected) == 1
    assert selected.iloc[0].time_from == 0.0
    assert selected.iloc[0].time_to == 162.243

    # Terminated
    selected = metrics[(metrics.verb == XAPI_VIDEO_VERB_TERMINATED)]
    assert len(selected) == 1
    assert selected.iloc[0].length == 119.931
    assert selected.iloc[0].time == 40


def test_select_metrics_for_verb():
    """Test select_metrics_for_verb utility"""

    metrics = pd.concat(
        [
            xAPIVideoMetricsFactory.build(count=2, verb=XAPI_VIDEO_VERB_SEEKED),
            xAPIVideoMetricsFactory.build(count=2, verb=XAPI_VIDEO_VERB_PLAYED),
        ]
    )
    assert len(metrics) == 4

    selected = select_metrics_for_verb(
        metrics, XAPI_VIDEO_VERB_PLAYED, unique=True, unique_by="actor"
    )
    assert len(selected) == 2
    assert selected.verb.values == [XAPI_VIDEO_VERB_PLAYED]


def test_select_metrics_for_verb_with_same_actor():
    """Test select_metrics_for_verb utility"""

    metrics = pd.concat(
        [
            xAPIVideoMetricsFactory.build(
                count=2, verb=XAPI_VIDEO_VERB_SEEKED, actor="foo"
            ),
            xAPIVideoMetricsFactory.build(
                count=2, verb=XAPI_VIDEO_VERB_PLAYED, actor="foo"
            ),
        ]
    )
    assert len(metrics) == 4

    selected = select_metrics_for_verb(
        metrics, XAPI_VIDEO_VERB_PLAYED, unique=True, unique_by="actor"
    )
    assert len(selected) == 1
    assert XAPI_VIDEO_VERB_PLAYED in selected.verb.values
    assert selected.iloc[0].actor == "foo"

    selected = select_metrics_for_verb(
        metrics, XAPI_VIDEO_VERB_SEEKED, unique=True, unique_by="actor"
    )
    assert len(selected) == 1
    assert XAPI_VIDEO_VERB_SEEKED in selected.verb.values
    assert selected.iloc[0].actor == "foo"

    selected = select_metrics_for_verb(metrics, XAPI_VIDEO_VERB_PLAYED, unique=False)
    assert len(selected) == 2
    assert selected.iloc[0].verb == XAPI_VIDEO_VERB_PLAYED
    assert selected.iloc[0].actor == "foo"
    assert selected.iloc[1].verb == XAPI_VIDEO_VERB_PLAYED
    assert selected.iloc[1].actor == "foo"

    selected = select_metrics_for_verb(metrics, XAPI_VIDEO_VERB_SEEKED, unique=False)
    assert len(selected) == 2
    assert selected.iloc[0].verb == XAPI_VIDEO_VERB_SEEKED
    assert selected.iloc[0].actor == "foo"
    assert selected.iloc[1].verb == XAPI_VIDEO_VERB_SEEKED
    assert selected.iloc[1].actor == "foo"
