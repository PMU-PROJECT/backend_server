class ServerException(Exception):
    message: str
    http_code: int

    def __init__(self, message: str, http_code: int) -> None:
        self.message: str = message
        self.http_code: int = http_code


class RaisedFrom:
    source_exception: Exception

    def __init__(self, source_exception: Exception) -> None:
        self.source_exception = source_exception


class BadUserRequest(ServerException):
    def __init__(self, message: str):
        super(BadUserRequest, self).__init__(message, 400)


class DatabaseError(ServerException, RaisedFrom):
    def __init__(self, source_exception: Exception):
        super(ServerException, self).__init__('Unhandled database exception raised!', 500)

        super(RaisedFrom, self).__init__(source_exception)
