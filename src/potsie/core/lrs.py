import logging

import requests

from .exceptions import PotsieLRSAPIError, PotsieLRSRecordParsingError
from .settings import LRS_AUTH_TOKEN, LRS_API_URL


logger = logging.getLogger(__name__)


class Statement:
    """An xAPI statement extracted from an LRS record"""

    def __init__(self, statement):
        self.id = None
        # Lazy black magic
        self.__dict__.update(statement)
        self.verb = self.verb["display"]["en-US"]

    @property
    def _result(self):
        if not hasattr(self, "result"):
            msg = f"Current '{self.verb}' statement {self.id} has no result"
            logger.warning(msg)
            raise PotsieLRSRecordParsingError(msg)
        return self.result

    @property
    def _context(self):
        if not hasattr(self, "context"):
            msg = f"Current '{self.verb}' statement {self.id} has no context"
            logger.warning(msg)
            raise PotsieLRSRecordParsingError(msg)
        return self.context

    @property
    def result_extensions(self):
        if "extensions" not in self._result:
            msg = f"Current '{self.verb}' statement {self.id} has no result extensions"
            logger.warning(msg)
            raise PotsieLRSRecordParsingError(msg)
        return self._result["extensions"]

    @property
    def context_extensions(self):
        if "extensions" not in self._context:
            msg = f"Current '{self.verb}' statement {self.id} has no context extensions"
            logger.warning(msg)
            raise PotsieLRSRecordParsingError(msg)
        return self._context["extensions"]


class Record:
    """An LRS record."""

    def __init__(self, record):
        self._id = None
        # Lazy black magic
        self.__dict__.update(record)
        self.statement = Statement(self.statement)


class VideoRecord(Record):
    """LRS record following the xAPI video statement specification.

    Reference:
    https://liveaspankaj.gitbooks.io/xapi-video-profile/statement_data_model.html
    """

    @property
    def length(self):
        return self.statement.context_extensions.get(
            "https://w3id.org/xapi/video/extensions/length", None
        )

    @property
    def time(self):
        return self.statement.result_extensions.get(
            "https://w3id.org/xapi/video/extensions/time", None
        )

    @property
    def speed(self):
        """Return λx speed string as a float(λ)."""
        speed = self.statement.context_extensions.get(
            "https://w3id.org/xapi/video/extensions/speed", None
        )
        if speed is None:
            return
        return float(speed.rstrip("x"))

    @property
    def time_from(self):
        return self.statement.result_extensions.get(
            "https://w3id.org/xapi/video/extensions/time-from", None
        )

    @property
    def time_to(self):
        return self.statement.result_extensions.get(
            "https://w3id.org/xapi/video/extensions/time-to", None
        )


def api(url=LRS_API_URL, auth_token=LRS_AUTH_TOKEN, verb="get", endpoint="", **kwargs):
    """Perform an HTTP request against the LRS API."""

    request_url = f"{url}/{endpoint}"

    logger.debug(f"New request started: {verb} {request_url} {kwargs}")

    response = getattr(requests, verb)(
        request_url, headers={"Authorization": f"Basic {auth_token}"}, **kwargs
    )
    if response.status_code != requests.codes.OK:
        msg = (
            f"LRS API '{verb}' request '{request_url}' failed! "
            f"Code: {response.status_code}, Content: {response.text}"
        )
        logger.error(msg)
        raise PotsieLRSAPIError(msg)

    logger.debug(f"Request ended: {response.status_code}")

    return response.json()


def get_objects_for_model(name, params):
    """Get all objects for a model name."""

    get_nodes = lambda edges: [edge.get("node") for edge in edges]

    response = api(endpoint=name, params=params)
    objects = get_nodes(response.get("edges"))

    # Handle pagination
    while response.get("pageInfo").get("hasNextPage"):
        params.update({"after": response.get("pageInfo").get("endCursor")})
        response = api(endpoint="statement", params=params)
        objects += get_nodes(response.get("edges"))

    return objects


def get_records(params={}):
    """Get all statements with given parameters."""

    return get_objects_for_model(name="statement", params=params)


def get_records_for_id(object_id):
    """Get all statements for a given object ID (an uuid is expected)."""

    params = {"filter": f'{{"$or": [{{"statement.object.id": "uuid://{object_id}"}}]}}'}
    return get_records(params=params)
