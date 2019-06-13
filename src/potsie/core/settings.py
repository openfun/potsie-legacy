from os import environ

from .exceptions import PotsieConfigurationError

# LRS related settings
LRS_AUTH_TOKEN = environ.get("POTSIE_LRS_AUTH_TOKEN", None)
if LRS_AUTH_TOKEN is None:
    raise PotsieConfigurationError(
        "POTSIE_LRS_AUTH_TOKEN environment variable should be defined"
    )

LRS_API_URL = environ.get("POTSIE_LRS_API_URL", None)
