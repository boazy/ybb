from dataclasses import dataclass
from enum import Enum
from typing import Self
from rich.console import Console

class ColorMode(str, Enum):
    always = "always"
    auto = "auto"
    off = "off"

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

# Global console instances
_consoles: Consoles | None = None

def initialize(color_mode: ColorMode) -> Consoles:
    """Initialize the global console instances based on color mode."""
    global _consoles
    consoles = Consoles.create(color_mode)
    _consoles = consoles
    return consoles

def get() -> Consoles:
    """Get the console instances."""
    global _consoles
    if _consoles:
        return _consoles
    else:
        # Default to auto mode if not initialized
        return initialize(ColorMode.auto)