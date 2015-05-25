__author__ = 'admin'

class UserAlreadyRegisteredError(Exception):
    def __init__(self, mismatch):
        Exception.__init__(self, 'Sorry, your email has been registered!')

class TicketSoldOutError(Exception):
    def __init__(self, mismatch):
        Exception.__init__(self, 'Sorry, all tickets sold out. We will contact you if extra tickets are available.')