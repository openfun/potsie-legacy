from potsie.core.lrs import get_records_for_id
from potsie.core.xapi import get_video_statements_metrics


def get_metrics_for_video_id(video_id):
    """Query video statements to the LRS and convert statements to metrics"""
    return get_video_statements_metrics(get_records_for_id(video_id))
