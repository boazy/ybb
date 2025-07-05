from dataclasses import dataclass
from enum import Enum
from typing import Self
from rich.console import Console

class ColorMode(str, Enum):
    always = "always"
    auto = "auto"
    off = "off"

# Global console instances
_console: Console | None = None
_error_console: Console | None = None

@dataclass(frozen=True)
class Consoles:
    main: Console
    error: Console

    @staticmethod
    def _create_console(color_mode: ColorMode, stderr: bool = False) -> Console:
        if color_mode == ColorMode.always:
            return Console(force_terminal=True, color_system="truecolor", stderr=stderr)
        elif color_mode == ColorMode.off:
            return Console(force_terminal=False, color_system=None, stderr=stderr)
        else:
            return Console(stderr=stderr)

    @classmethod
    def create(cls: type[Self], color_mode: ColorMode) -> Self:
        return cls(
            main=cls._create_console(color_mode),
            error=cls._create_console(color_mode, stderr=True)
        )

    def _register_globals(self) -> None:
        global _console, _error_console
        _console = self.main
        _error_console = self.error

def initialize_console(color_mode: ColorMode) -> Consoles:
    """Initialize the global console instances based on color mode."""
    global _console, _error_console

    consoles = Consoles.create(color_mode)
    consoles._register_globals()
    return consoles

def get_console() -> Console:
    """Get the global console instance."""
    if _console is None:
        # Default to auto mode if not initialized
        return initialize_console(ColorMode.auto).main
    return _console

def get_error_console() -> Console:
    """Get the global error console instance."""
    if _error_console is None:
        # Default to auto mode if not initialized
        return initialize_console(ColorMode.auto).error
    return _error_console