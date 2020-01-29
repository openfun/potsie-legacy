import logging
from dataclasses import asdict, dataclass
from typing import List

import pandas as pd

from .exceptions import PotsieLRSRecordParsingError
from .lrs import VideoRecord

logger = logging.getLogger(__name__)


XAPI_VIDEO_VERB_COMPLETED = "completed"
XAPI_VIDEO_VERB_INITIALIZED = "initialized"
XAPI_VIDEO_VERB_INTERACTED = "interacted"
XAPI_VIDEO_VERB_PAUSED = "paused"
XAPI_VIDEO_VERB_PLAYED = "played"
XAPI_VIDEO_VERB_SEEKED = "seeked"
XAPI_VIDEO_VERB_TERMINATED = "terminated"

XAPI_VIDEO_VERBS = (
    XAPI_VIDEO_VERB_COMPLETED,
    XAPI_VIDEO_VERB_INITIALIZED,
    XAPI_VIDEO_VERB_INTERACTED,
    XAPI_VIDEO_VERB_PAUSED,
    XAPI_VIDEO_VERB_PLAYED,
    XAPI_VIDEO_VERB_SEEKED,
    XAPI_VIDEO_VERB_TERMINATED,
)

XAPI_VIDEO_DEFAULT_SPEED = 1.0

XAPI_VIDEO_SPEED_VALUES = (0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0)


@dataclass
class xAPIVideoMetric:
    """Base data collected from xAPI video statements."""

    _id: str
    timestamp: str
    verb: str
    actor: str
    object_id: str
    length: float = None
    speed: float = XAPI_VIDEO_DEFAULT_SPEED
    time: float = None
    time_from: float = None
    time_to: float = None


@dataclass
class xAPIVideoMetrics:
    """Base data collected from xAPI video statements."""

    metrics: List[xAPIVideoMetric]


def get_video_statements_metrics(records):
    """Extract metrics from xAPI statements video data model."""

    video_metrics = xAPIVideoMetrics([])

    # Collect relevant fields
    for entry in records:

        record = VideoRecord(entry)

        verb = record.statement.verb
        metric = xAPIVideoMetric(
            _id=record.statement.id,
            timestamp=record.statement.timestamp,
            verb=verb,
            actor=record.statement.actor["account"]["name"],
            object_id=record.statement.object["id"],
        )

        if verb == XAPI_VIDEO_VERB_COMPLETED:
            metric.length = record.length
            metric.time = record.time

        elif verb == XAPI_VIDEO_VERB_INITIALIZED:
            metric.length = record.length
            metric.speed = record.speed or XAPI_VIDEO_DEFAULT_SPEED

        elif verb == XAPI_VIDEO_VERB_INTERACTED:
            metric.speed = record.speed or XAPI_VIDEO_DEFAULT_SPEED
            # Some old xAPI events implementation does NOT ship "time" in result
            # extensions
            try:
                metric.time = record.time
            except PotsieLRSRecordParsingError:
                pass

        elif verb == XAPI_VIDEO_VERB_PAUSED:
            metric.length = record.length
            metric.time = record.time

        elif verb == XAPI_VIDEO_VERB_PLAYED:
            metric.time = record.time

        elif verb == XAPI_VIDEO_VERB_SEEKED:
            metric.time_from = record.time_from
            metric.time_to = record.time_to

        elif verb == XAPI_VIDEO_VERB_TERMINATED:
            metric.length = record.length
            metric.time = record.time

        video_metrics.metrics.append(metric)

    # Convert metrics to DataFrame with timestamps as sorted datetime objects
    video_metrics = pd.DataFrame(asdict(video_metrics).get("metrics", None))
    video_metrics["timestamp"] = pd.to_datetime(video_metrics["timestamp"])
    return video_metrics.set_index("timestamp").sort_values(by=["timestamp"])


def select_metrics_for_verb(metrics, verb, unique=True, unique_by="actor"):
    """Select metrics for a verb.

    If unique is True (default), it returns unique metrics for a verb per actor,
    else, you can inactivate the unique filter and choose another column for
    uniqueness via the unique_by keyword argument.
    """

    metrics = metrics[(metrics.verb == verb)]
    if unique:
        return metrics.drop_duplicates(unique_by)
    return metrics


def make_distribution_for_verb(
    metrics, verb, group_by=pd.Grouper(freq="D"), unique=True
):
    """Make a distribution for a verb given a group_by criterion."""
    return (
        select_metrics_for_verb(metrics, verb, unique=unique)
        .groupby(by=group_by)
        .count()
    )
