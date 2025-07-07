import typer
import logging
from typing import List, Optional
from rich.table import Table
from ..yabai import yabai, YabaiError, DisplaySelector
from ..data_types import Window
from .. import console as ybb_console


# Column width constants
SPACE_WIDTH = 12
DISPLAY_WIDTH = 5
ID_WIDTH = 8
LAYER_WIDTH = 8
SUB_LAYER_WIDTH = 10
FLAGS_WIDTH = 5
APP_MIN_WIDTH = 8


def _generate_flags(window: Window) -> str:
    """Generate flag string for a window with 5 slots: R, A, H/M/V, N/Z/z, F/S."""
    flags = [' ', ' ', ' ', ' ', ' ']
    
    # Slot 0: R (Root Window)
    if window.root_window:
        flags[0] = 'R'
    
    # Slot 1: A (Active, has-focus)
    if window.has_focus:
        flags[1] = 'A'
    
    # Slot 2: H/M/V (Hidden, Minimized, Visible - by priority)
    if window.is_hidden:
        flags[2] = 'H'
    elif window.is_minimized:
        flags[2] = 'M'
    elif window.is_visible:
        flags[2] = 'V'
    
    # Slot 3: N/Z/z (Native Fullscreen, Full Screen Zoom, Parent Zoom)
    if window.is_native_fullscreen:
        flags[3] = 'N'
    elif window.has_fullscreen_zoom:
        flags[3] = 'Z'
    elif window.has_parent_zoom:
        flags[3] = 'z'
    
    # Slot 4: F/S (Floating, Sticky)
    if window.is_floating:
        flags[4] = 'F'
    elif window.is_sticky:
        flags[4] = 'S'
    
    return ''.join(flags)


def _calculate_column_widths(windows: List[Window], terminal_width: int, 
                           show_space: bool, show_display: bool) -> tuple[int, int]:
    """Calculate responsive column widths for App and Title columns."""
    # Calculate fixed column widths
    fixed_width = 0
    
    # ID column
    fixed_width += ID_WIDTH
    
    # Space column
    if show_space:
        fixed_width += SPACE_WIDTH
    
    # Display column
    if show_display:
        fixed_width += DISPLAY_WIDTH
    
    # Layer column
    fixed_width += LAYER_WIDTH
    
    # Sub-layer column
    fixed_width += SUB_LAYER_WIDTH
    
    # Flags column
    fixed_width += FLAGS_WIDTH
    
    # Account for table borders and padding (roughly 2 chars per column)
    num_columns = 7 - (0 if show_space else 1) - (0 if show_display else 1)
    fixed_width += num_columns * 2

    longest_app_name = max(len(window.app) for window in windows)
    max_app_width = max(longest_app_name, APP_MIN_WIDTH)
    longest_title = max(len(window.title) for window in windows)
    # Available width for App and Title
    available_width = max(terminal_width - fixed_width, 20)
    
    # App gets minimum APP_MIN_WIDTH chars, Title gets the rest
    # App grows at 25% of the rate that Title grows
    # So if we have X chars available: App = APP_MIN_WIDTH + 0.25 * (X - APP_MIN_WIDTH) / 1.25, Title = (X - APP_MIN_WIDTH) / 1.25
    if available_width <= APP_MIN_WIDTH:
        app_width = available_width
        title_width = 0
    else:
        remaining = available_width - APP_MIN_WIDTH
        title_base = int(remaining / 1.25)
        app_additional = int(remaining - title_base)
        
        app_desired_width = APP_MIN_WIDTH + app_additional
        app_width = min(app_desired_width, max_app_width)
        app_overflow = app_desired_width - app_width
        title_width = min(title_base + app_overflow, longest_title)
    
    return app_width, title_width


def _truncate_text(text: str, max_width: int) -> str:
    """Truncate text with ellipsis if it exceeds max_width."""
    if len(text) <= max_width:
        return text
    if max_width <= 1:
        return text[:max_width]
    return text[:max_width - 1] + '…'


def table_command(display: Optional[DisplaySelector] = None, space: Optional[str] = None):
    """Create a table layout of windows."""
    try:
        # Get terminal width
        console_obj = ybb_console.get()
        terminal_width = console_obj.main.size.width
        
        # Determine filtering and column visibility
        show_space = space is None
        show_display = display is None
        
        # Query windows based on filters
        if space is not None:
            windows = yabai.query.windows(space=space)
        elif display is not None:
            windows = yabai.query.windows(display=display)
        else:
            windows = yabai.query.windows()
        
        if not windows:
            logging.warning("No windows found.")
            return
        
        # Get spaces for space index mapping if needed
        spaces_by_id = {}
        if show_space:
            spaces = yabai.query.spaces()
            spaces_by_id = {s.id: s for s in spaces}
        
        # Calculate column widths
        app_width, title_width = _calculate_column_widths(
            windows, terminal_width, show_space, show_display
        )
        
        # Create table
        table = Table(show_header=True, header_style="bold blue")
        
        # Add columns based on visibility
        if show_space:
            table.add_column("Space", width=SPACE_WIDTH, justify="left")
        if show_display:
            table.add_column("Disp", width=DISPLAY_WIDTH, justify="right")
        
        table.add_column("Id", width=ID_WIDTH, justify="right")
        table.add_column("App", width=app_width, no_wrap=True)
        table.add_column("Title", width=max(title_width, 5), no_wrap=True, justify="left")
        table.add_column("Layer", width=LAYER_WIDTH)
        table.add_column("Sublayer", width=SUB_LAYER_WIDTH)
        table.add_column("Flags", width=FLAGS_WIDTH)
        
        # Add rows
        for window in windows:
            row = []
            
            # Space column
            if show_space:
                if window.space in spaces_by_id:
                    space_info = spaces_by_id[window.space]
                    space_text = f"{space_info.id} ({space_info.index})"
                else:
                    space_text = str(window.space)
                row.append(space_text)
            
            # Display column
            if show_display:
                row.append(str(window.display))
            
            # Fixed columns
            row.append(str(window.id))
            row.append(_truncate_text(window.app, app_width))
            row.append(_truncate_text(window.title, title_width))
            row.append(window.layer)
            row.append(window.sub_layer)
            row.append(_generate_flags(window))
            
            table.add_row(*row)
        
        # Print table
        console_obj.main.print(table)
        
    except YabaiError as e:
        logging.error(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1)