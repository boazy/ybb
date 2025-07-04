from enum import Enum
from rich.console import Console

class ColorMode(str, Enum):
    always = "always"
    auto = "auto"
    off = "off"

# Global console instances
_console: Console | None = None
_error_console: Console | None = None

def initialize_console(color_mode: ColorMode) -> None:
    """Initialize the global console instances based on color mode."""
    global _console, _error_console
    
    if color_mode == ColorMode.always:
        # Force color output with truecolor support
        _console = Console(force_terminal=True, color_system="truecolor")
        _error_console = Console(stderr=True, force_terminal=True, color_system="truecolor")
    elif color_mode == ColorMode.off:
        # Disable all color output
        _console = Console(force_terminal=False, color_system=None)
        _error_console = Console(stderr=True, force_terminal=False, color_system=None)
    else:  # auto
        # Let Rich auto-detect terminal capabilities
        _console = Console()
        _error_console = Console(stderr=True)

def get_console() -> Console:
    """Get the global console instance."""
    if _console is None:
        # Default to auto mode if not initialized
        initialize_console(ColorMode.auto)
    return _console

def get_error_console() -> Console:
    """Get the global error console instance."""
    if _error_console is None:
        # Default to auto mode if not initialized
        initialize_console(ColorMode.auto)
    return _error_console