__author__ = 'admin'

class UserAlreadyRegisteredError(Exception):
    def __init__(self, mismatch):
        Exception.__init__(self, mismatch)

class EmailAddressFormatError(Exception):
    def __init__(self, mismatch):
        Exception.__init__(self, mismatch)