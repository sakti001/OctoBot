"""
Octeon stuff
"""
class message:
    """
    Base message class

    Raises:
        TypeError on incompatible conditions, like photo and parse_mode
    """
    def __init__(text="", photo=None, inline_keyboard=None, parse_mode=None):
        self.text = text
        self.photo = photo
        self.inline_keyboard = inline_keyboard
        self.parse_mode = parse_mode
        if photo and parse_mode:
            raise TypeError("parse_mode and photo cant be used at same time!")
