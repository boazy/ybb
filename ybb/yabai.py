from __future__ import annotations
import subprocess
import logging
from typing import Any, List, Literal, Optional

from ybb.data_types import InsertDirection, Space as RawSpace, Window as RawWindow

logger = logging.getLogger('yabai')

class YabaiError(Exception):
    """Raised when a yabai command fails."""
    pass

def call(args: List[str]) -> str:
    """
    A low-level function that wraps calling all yabai commands.

    Args:
        args: A list of strings representing the command and its arguments.

    Returns:
        The stdout returned by yabai

    Raises:
        YabaiError: If the yabai command returns a non-zero exit code
    """
    logger.debug(f"[bright_black]> yabai {' '.join(args)}[/bright_black]")
    try:
        result = subprocess.run(["yabai"] + args, capture_output=True, text=True, check=True)
        if result.stdout:
            return result.stdout.strip()
        else:
            return ""
    except subprocess.CalledProcessError as e:
        raise YabaiError(f"Yabai command failed: {e.stderr}") from e

WindowSelector = int | str
SpaceSelector =  int | str

class Query:
    def __init__(self, parent: Yabai):
        self._parent = parent

    def window(self, window: Optional[WindowSelector] = None) -> Optional[RawWindow]:
        """
        Queries for a single window.

        Args:
            window: A window selector.
        """

        command = ["-m", "query", "--windows", "--window"]

        if window is not None and window != "focused":
            command.append(str(window))

        result = self._parent.call(command)
        if result:
            return RawWindow.from_json(result)
        return None

    def windows(self, window: Optional[WindowSelector] = None, space: Optional[SpaceSelector] = None) -> List[RawWindow]:
        """
        Queries for windows.

        Args:
            window: A window selector. Returns a single window wrapped in a list.
            space: A space selector. Returns a list of windows.

        Returns:
            A list of window dictionaries.
        """
        if window and space:
            raise ValueError("Cannot specify both 'window' and 'space' selectors.")

        command = ["-m", "query", "--windows"]
        is_single_item = bool(window)

        if window:
            if window != "focused":
                command.extend(["--window", str(window)])
            elif window is not None:
                command.append("--window")
        elif space:
            if space != "focused":
                command.extend(["--space", str(space)])
            elif space is not None:
                command.append("--space")

        result = self._parent.call(command)

        if is_single_item:
            return [RawWindow.from_json(result)]

        return RawWindow.schema().loads(result, many=True)

    def space(self, space: Optional[SpaceSelector] = None) -> Optional[RawSpace]:
        """
        Queries for a single space.
        """
        command = ["-m", "query", "--spaces", "--space"]
        if space is not None and space != "focused":
            command.append(str(space))
        elif space is not None:
            command.append("--space")
        result = self._parent.call(command)
        if result:
            return RawSpace.from_json(result)
        return None

    def spaces(self, space: Optional[SpaceSelector] = None) -> List[RawSpace]:
        """
        Queries for spaces.

        Args:
            space: A space selector. If provided, returns a single space wrapped in a list.

        Returns:
            A list of space dictionaries.
        """
        command = ["-m", "query", "--spaces"]
        is_single_item = bool(space)

        if space:
            if space != "focused":
                command.extend(["--space", str(space)])
            else:
                command.append("--space")

        result = self._parent.call(command)

        if not result:
            return []

        if is_single_item:
            return [RawSpace.from_json(result)]

        return RawSpace.schema().loads(result, many=True)

class Space:
    def __init__(self, parent):
        self._parent = parent

    def layout(self, layout: str, space: Optional[int] = None):
        command = ["-m", "space"]
        if space:
            command.append(str(space))
        command.extend(["--layout", layout])
        return self._parent.call(command)

class Window:
    def __init__(self, parent, window: Optional[WindowSelector] = None):
        self._parent = parent
        self._window = window

    def __call__(self, window: Optional[WindowSelector] = None):
        return Window(self._parent, window)

    def _call_window(self, command: List[str]):
        full_command = ["-m", "window"]
        if self._window and self._window != 'focused':
            full_command.append(str(self._window))
        full_command.extend(command)
        return self._parent.call(full_command)

    def focus(self):
        return self._call_window(["--focus"])

    def resize(self, window_selector: str, axis: str, delta_x: int, delta_y: int):
        return self._call_window(["--resize", f"{axis}:{delta_x}:{delta_y}"])

    def stack(self, target_window: Optional[WindowSelector] = None):
        return self._call_window(["--stack", str(target_window)])

    def insert(self, direction: InsertDirection):
        """Set the splitting mode of the selected window."""
        return self._call_window(["--insert", direction.value])
    
    def ratio(self, type: Literal["abs", "rel"], ratio: float):
        """Set the split ratio for the window."""
        return self._call_window(["--ratio", f"{type}:{ratio}"])

    def toggle(self, option: str):
        return self._call_window(["--toggle", option])
    
    def warp(self, target_window: WindowSelector, insert_direction: Optional[InsertDirection] = None):
        """Warp the window to the specified location."""
        if insert_direction:
            # Set insert direction on the target window
            self._parent.window(target_window).insert(insert_direction)
        return self._call_window(["--warp", str(target_window)])

class Yabai:
    def __init__(self):
        self.query = Query(self)
        self.space = Space(self)
        self.window = Window(self)

    def call(self, args: List[str]) -> Any:
        return call(args)

yabai = Yabai()
