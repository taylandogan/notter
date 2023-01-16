class NotterException(Exception):
    message = "Something went wrong, please inform the maintainer"


class NoteNotFound(NotterException):
    message = "Could not find that note"


class NoteAlreadyExists(NotterException):
    message = "That node already exists"
