from fastapi import HTTPException, status


class CredentialsException(HTTPException):
    """
    Exception raised when credentials could not be validated.
    """

    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
