import requests

from .exceptions import PotsieLRSAPIError
from .settings import LRS_AUTH_TOKEN, LRS_API_URL


def api(url=LRS_API_URL, auth_token=LRS_AUTH_TOKEN, verb="get", endpoint="", **kwargs):
    """Perform an HTTP request against the LRS API."""

    request_url = f"{url}/{endpoint}"
    response = getattr(requests, verb)(
        request_url, headers={"Authorization": f"Basic {auth_token}"}, **kwargs
    )
    if response.status_code != requests.codes.OK:
        raise PotsieLRSAPIError(
            f"LRS API '{verb}' request '{request_url}' failed! "
            f"Code: {response.status_code}, Content: {response.text}"
        )
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


def get_statements(params={}):
    """Get all statements with given parameters."""

    return get_objects_for_model(name="statement", params=params)


def get_statements_for_id(object_id):
    """Get all statements for a given object ID (an uuid is expected)."""

    params = {"filter": f'{{"$or": [{{"statement.object.id": "uuid://{object_id}"}}]}}'}
    return get_statements(params=params)
