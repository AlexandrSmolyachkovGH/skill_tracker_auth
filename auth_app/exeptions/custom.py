class AttrError(ValueError):
    pass


class TokenError(ValueError):
    pass


class UserVerificationError(ValueError):
    """
    Error with verification user record status
    """

    def __init__(self) -> None:
        message = "The user's record must be verified"
        super().__init__(message)


class UserActivityError(ValueError):
    """
    Error in activity status of user
    """

    def __init__(self) -> None:
        message = "The user's record must be active"
        super().__init__(message)
