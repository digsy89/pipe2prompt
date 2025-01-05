import logging

# ANSI color codes
COLORS = {
    'black': '\033[30m',
    'red': '\033[31m',
    'green': '\033[32m', 
    'yellow': '\033[33m',
    'blue': '\033[34m',
    'magenta': '\033[35m',
    'cyan': '\033[36m',
    'white': '\033[37m',
    'bright_black': '\033[90m',
    'bright_red': '\033[91m',
    'bright_green': '\033[92m',
    'bright_yellow': '\033[93m', 
    'bright_blue': '\033[94m',
    'bright_magenta': '\033[95m',
    'bright_cyan': '\033[96m',
    'bright_white': '\033[97m',
    'reset': '\033[0m'
}

def highlight(text: str, color: str = 'magenta') -> str:
    return f"{COLORS[color]}{text}{COLORS['reset']}"


# Custom formatter to add color to the log level
class ColoredFormatter(logging.Formatter):
    def format(self, record):
        levelname = record.levelname
        if levelname == 'ERROR':
            record.levelname = f"{COLORS['red']}{levelname}{COLORS['reset']}"
        elif levelname == 'WARNING':
            record.levelname = f"{COLORS['yellow']}{levelname}{COLORS['reset']}"
        return super().format(record)

def get_logger(name: str) -> logging.Logger:
    # Create a handler with the colored formatter
    handler = logging.StreamHandler()
    formatter = ColoredFormatter('%(levelname)s %(message)s')
    handler.setFormatter(formatter)

    # Get the logger and add the handler
    logger = logging.getLogger(name)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)  # Set the desired log level
    return logger
