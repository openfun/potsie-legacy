from pandas.core.dtypes.dtypes import DatetimeTZDtype

from ..lrs import get_records_for_id
from ..xapi import get_video_statements_metrics


def test_get_video_statements_metrics():
    """Test get_video_statements_metrics"""

    video_id = "126bd2fb-a846-cd73-2278-fedf9861560b"
    statements = get_records_for_id(video_id)
    metrics = get_video_statements_metrics(statements)
    assert len(metrics) == 29
    assert type(metrics["timestamp"].dtype) == DatetimeTZDtype
