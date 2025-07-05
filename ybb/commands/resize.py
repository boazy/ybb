import typer
import logging
from ..yabai import yabai, YabaiError
from ..data_types import SplitType
from ..tree import reconstruct_tree

def resize_command(
    increment: int = typer.Argument(...),
    window: str = typer.Option("focused", "--window", "-w", help="Window to resize.")
):
    """
    Smart resize for a window.
    """
    try:
        # Get all windows for the current space to reconstruct the tree
        all_windows_data = yabai.query.windows(space="focused")
        if not all_windows_data:
            logging.error("[red]Error:[/red] No windows found in the current space.")
            raise typer.Exit(code=1)

        # Reconstruct the BSP tree
        bsp_tree = reconstruct_tree(all_windows_data)
        if not bsp_tree:
            logging.error("[red]Error:[/red] Could not reconstruct BSP tree for the current space.")
            raise typer.Exit(code=1)

        # Find the target window and its parent in the tree
        target_window_data = yabai.query.window(window)
        if not target_window_data:
            logging.error(f"[red]Error:[/red] Could not find window: {window}")
            raise typer.Exit(code=1)
        target_window_id = target_window_data.id

        found_node = bsp_tree.find_window(target_window_id)

        if not found_node:
            logging.error(f"[red]Error:[/red] Window {target_window_id} not found in the BSP tree.")
            raise typer.Exit(code=1)

        # Get the parent split (closest ancestor that is an instance of Split)
        if not found_node.ancestors:
            logging.error(f"[red]Error:[/red] Window {target_window_id} has no parent split to resize. (root nodes cannot be resized)")
            raise typer.Exit(code=1)
        
        parent_split = found_node.ancestors[-1]  # Last ancestor (closest parent)
        is_first_child = found_node.is_first_child
        
        # Determine axis and delta based on parent split type and child position
        # For BSP node fences, we need to drag the edge facing the split
        if parent_split.split_type == SplitType.VERTICAL:
            if is_first_child:
                # First child (left side) - drag right edge, positive delta expands right
                axis = "right"
                delta_x = increment
                delta_y = 0
            else:
                # Second child (right side) - drag left edge, negative delta expands left
                axis = "left" 
                delta_x = -increment  # Negative to expand toward the split
                delta_y = 0
        else:  # SplitType.HORIZONTAL
            if is_first_child:
                # First child (top side) - drag bottom edge, positive delta expands down
                axis = "bottom"
                delta_x = 0
                delta_y = increment
            else:
                # Second child (bottom side) - drag top edge, negative delta expands up
                axis = "top"
                delta_x = 0
                delta_y = -increment  # Negative to expand toward the split

        # Call yabai to resize the window
        logging.debug(f"Resizing window {target_window_id}: axis={axis}, delta_x={delta_x}, delta_y={delta_y}")
        yabai.window(target_window_id).resize("", axis, delta_x, delta_y)

    except YabaiError as e:
        logging.error(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1)
