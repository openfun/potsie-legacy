from ..lrs import get_records_for_id


def test_get_records_for_id():
    """Test get_statements_for_id"""

    video_id = "4a295fd3-0b47-7c7b-ffe3-4ade04c2075b"
    statements = get_records_for_id(video_id)
    assert len(statements) == 29
