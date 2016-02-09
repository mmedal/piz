class DependencyNotSatisfiedError(Exception):
    pass


class DownloadSubprocessError(Exception):
    pass


class UserMisconfigurationError(Exception):
    pass


class ParseError(Exception):
    pass


class NoResultsFound(Exception):
    pass
