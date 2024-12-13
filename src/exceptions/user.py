from src.exceptions.base import CloudsellIDException


class UserNotFound(CloudsellIDException):
    ...

class AuthorizationException(CloudsellIDException):
    ...

class AuthenticationException(CloudsellIDException):
    ...

class UserAlreadyExists(CloudsellIDException):
    ...