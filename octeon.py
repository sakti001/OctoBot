"""
Octeon stuff
"""

class message:
    """
    Base message class

    Raises:
        TypeError on incompatible conditions, like photo and parse_mode
    """
    def __init__(self,
                 text="", 
                 photo=None, 
                 inline_keyboard=None, 
                 parse_mode=None,
                 failed=False):
        self.text = text
        self.failed = failed
        self.photo = photo
        self.inline_keyboard = inline_keyboard
        self.parse_mode = parse_mode
        if photo and parse_mode:
            raise TypeError("parse_mode and photo cant be used at same time!")

class Plugin:
    """Octeon plugin base"""
    def __init__(self):
        self.commands = []
    
    def command(self, command, description, inline_supported=True):
        def tags_decorator(func):
            self.commands.append({
                "command":command,
                "description":description,
                "function":func,
                "inline_support":inline_supported
            })
        return tags_decorator
