import json
import pytest

from ..exceptions import PotsieLRSRecordParsingError
from ..lrs import get_records_for_id, Record, Statement, VideoRecord

from . import (
    FIXTURES_COMPLETED_RECORD_PATH,
    FIXTURES_INITIALIZED_RECORD_PATH,
    FIXTURES_INTERACTED_RECORD_PATH,
    FIXTURES_PAUSED_RECORD_PATH,
    FIXTURES_PLAYED_RECORD_PATH,
    FIXTURES_SEEKED_RECORD_PATH,
    FIXTURES_TERMINATED_RECORD_PATH,
)


class TestStatement:
    """Test cases for the Statement object."""

    def test_result_extensions_property(self):
        """Test Statement parsing via the result_extensions property."""

        with open(FIXTURES_PLAYED_RECORD_PATH) as fixture:
            statement = Statement(json.load(fixture)["statement"])
        expected = {"https://w3id.org/xapi/video/extensions/time": 148.774}
        assert statement.result_extensions == expected

    def test_result_extensions_property_without_result(self):
        """Ensure an exception is raised when the current statement has no result extensions."""

        with open(FIXTURES_INITIALIZED_RECORD_PATH) as fixture:
            statement = Statement(json.load(fixture)["statement"])
        with pytest.raises(PotsieLRSRecordParsingError) as excinfo:
            statement.result_extensions
        expected = "Current 'initialized' statement 231754e7-13b9-4bb9-ab51-9a35686b4242 has no result"
        assert str(excinfo.value) == expected

    def test_context_extensions_property(self):
        """Test Statement parsing via the context_extensions property."""

        with open(FIXTURES_INTERACTED_RECORD_PATH) as fixture:
            statement = Statement(json.load(fixture)["statement"])

        assert (
            "https://w3id.org/xapi/video/extensions/speed"
            in statement.context_extensions
        )


class TestRecord:
    """Test cases for the Record object."""

    def test_record_statement_initialization(self):
        """Test the record statement is properly initialized"""

        with open(FIXTURES_PLAYED_RECORD_PATH) as fixture:
            record = Record(json.load(fixture))
        assert record._id is not None
        assert isinstance(record.statement, Statement)


class TestVideoRecord:
    """Test cases for the VideoRecord object."""

    def test_video_record_length_property(self):
        """Test video record length property"""

        with open(FIXTURES_PAUSED_RECORD_PATH) as fixture:
            record = VideoRecord(json.load(fixture))
        assert record.length == 291.108

    def test_video_record_time_property(self):
        """Test video record time property"""

        with open(FIXTURES_PLAYED_RECORD_PATH) as fixture:
            record = VideoRecord(json.load(fixture))
        assert record.time == 148.774

    def test_video_record_time_property_for_verb_with_no_time(self):
        """Test video record time property for a verb with no result/time extension"""

        with open(FIXTURES_INTERACTED_RECORD_PATH) as fixture:
            record = VideoRecord(json.load(fixture))
        with pytest.raises(PotsieLRSRecordParsingError) as excinfo:
            record.time
        expected = "Current 'interacted' statement 302c3e13-8d51-4463-98c5-6d3efd2bda65 has no result"
        assert str(excinfo.value) == expected

    def test_video_record_speed_property(self):
        """Test video record speed property"""

        with open(FIXTURES_INTERACTED_RECORD_PATH) as fixture:
            record = VideoRecord(json.load(fixture))
        assert record.speed == 1.0

    def test_video_record_speed_property_with_no_speed(self):
        """Test video record speed property for a verb with no context/speed extension"""

        with open(FIXTURES_PLAYED_RECORD_PATH) as fixture:
            record = VideoRecord(json.load(fixture))
        assert record.speed is None

    def test_video_record_time_from_property(self):
        """Test video record time_from property"""

        with open(FIXTURES_SEEKED_RECORD_PATH) as fixture:
            record = VideoRecord(json.load(fixture))
        assert record.time_from == 0

    def test_video_record_time_from_property_for_verb_with_no_time_from(self):
        """Test video record time_from property for a verb with no result/time_from extension"""

        with open(FIXTURES_INTERACTED_RECORD_PATH) as fixture:
            record = VideoRecord(json.load(fixture))
        with pytest.raises(PotsieLRSRecordParsingError) as excinfo:
            record.time_from
        expected = "Current 'interacted' statement 302c3e13-8d51-4463-98c5-6d3efd2bda65 has no result"
        assert str(excinfo.value) == expected

    def test_video_record_time_to_property(self):
        """Test video record time_to property"""

        with open(FIXTURES_SEEKED_RECORD_PATH) as fixture:
            record = VideoRecord(json.load(fixture))
        assert record.time_to == 162.243

    def test_video_record_time_to_property_for_verb_with_no_time_to(self):
        """Test video record time_to property for a verb with no result/time_to extension"""

        with open(FIXTURES_INTERACTED_RECORD_PATH) as fixture:
            record = VideoRecord(json.load(fixture))
        with pytest.raises(PotsieLRSRecordParsingError) as excinfo:
            record.time_to
        expected = "Current 'interacted' statement 302c3e13-8d51-4463-98c5-6d3efd2bda65 has no result"
        assert str(excinfo.value) == expected
