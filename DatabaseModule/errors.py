class ValidationError(ValueError):
    """The input failed validation."""


class DuplicateError(ValueError):
    """A unique value (such as an email) is already in use."""