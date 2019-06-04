import datetime
import pandas as pd


def get_video_statements_metrics(statements):
    """Extract metrics from xAPI statements video data model."""

    metrics = {"id": [], "timestamp": [], "verb": [], "actor": [], "object_id": []}

    # Collect relevant fields
    for statement in statements:
        metrics["id"].append(statement["_id"])
        metrics["timestamp"].append(statement["timestamp"])
        metrics["verb"].append(statement["statement"]["verb"]["display"]["en-US"])
        metrics["actor"].append(statement["statement"]["actor"]["account"]["name"])
        metrics["object_id"].append(statement["statement"]["object"]["id"])

    # Convert metrics to DataFrame with timestamps as sorted datetime objects
    metrics["timestamp"] = pd.to_datetime(metrics["timestamp"])
    metrics = (
        pd.DataFrame(metrics)
        .sort_values(by=["timestamp"])
        .set_index(pd.DatetimeIndex(metrics["timestamp"]))
    )
    return metrics


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
