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
                 file=None,
                 inline_keyboard=None, 
                 parse_mode=None,
                 failed=False):
        self.text = text
        self.file = file
        self.failed = failed
        self.photo = photo
        self.inline_keyboard = inline_keyboard
        self.parse_mode = parse_mode
        if (photo or file) and parse_mode:
            raise TypeError("parse_mode and photo/file cant be used at same time!")

class Plugin:
    """Octeon plugin base"""
    def __init__(self):
        self.commands = []
        self.handlers = []
    
    def command(self, command, description="", inline_supported=True, hidden=False):
        def decorator(func):
            self.commands.append({
                "command":command,
                "description":description,
                "function":func,
                "inline_support":inline_supported,
                "hidden":hidden
            })
        return decorator
    
    def message(self, regex:str):
        """
        Pass regex pattern for your function
        Disclaimer: this may work in Octeon-Discord
        """
        def decorator(func):
            self.handlers.append({
                "regex":regex,
                "function":func,
            })
        return decorator
