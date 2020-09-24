class PotsieConfigurationError(Exception):
    """Exception raised for Potsie configuration errors."""

    pass


class PotsieLRSAPIError(Exception):
    """Exception raised for LRS query errors."""

    pass


class PotsieLRSRecordParsingError(Exception):
    """Exception raised upon an LRS record parsing errors."""

    pass
