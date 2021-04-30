class TagNotFoundError(BaseException):
    """Exception raised if no open tag of selected type is found in the current selection, or at least one
    closing tag is missing.

    Attributes:
        expression -- input expression in which the error occurred
        message -- explanation of the error
    """

    def __init__(self, expression, message):
        self.expression = expression
        self.message = message