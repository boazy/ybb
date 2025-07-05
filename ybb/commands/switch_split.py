import typer
import logging
from ..yabai import yabai, YabaiError
from ..tree import WindowContext
from ..data_types import SplitType
from ..tree import reconstruct_tree

# Note: This doesn't really work well with Yabai.
def _switch_split_direction(found_node: WindowContext):
    """
    Switch the split direction of consecutive split siblings.
    
    This function finds all consecutive split siblings of the target window
    and recreates them as splits in the opposite axis direction.
    """
    consecutive_siblings = found_node.consecutive_split_siblings()

    if len(consecutive_siblings) <= 1:
        logging.warning("[yellow]Warning:[/yellow] No consecutive split siblings found to switch.")
        return
    
    # Determine the current split type from the ancestors
    if not found_node.ancestors:
        logging.error("[red]Error:[/red] Cannot switch split direction for root window.")
        raise typer.Exit(code=1)
    
    # Get the direct parent split to determine current split type
    direct_parent_split = found_node.ancestors[-1]
    current_split_type = direct_parent_split.split_type
    
    # Determine the new split type (opposite of current)
    new_split_type = SplitType.HORIZONTAL if current_split_type == SplitType.VERTICAL else SplitType.VERTICAL
    
    # Get the insertion direction for the new split type
    start_direction = new_split_type.start_direction()
    append_direction = start_direction.opposite()
    
    logging.debug(f"[blue]Debug:[/blue] Switching from {current_split_type.value} to {new_split_type.value}")
    logging.debug(f"[blue]Debug:[/blue] Found {len(consecutive_siblings)} consecutive siblings")
    
    # Get window IDs in order
    window_ids = [w.id for w in consecutive_siblings]
    
    # We need to recreate the split structure in the opposite axis
    # Start with the first window as the base
    target_window_id = window_ids[0]

    # First, check if any windows are in stacks that need to be unstacked
    # For a proper implementation, we might need to handle stacks, but for now
    # we'll work with the assumption that we're dealing with individual windows

    # Switch the first window twice
    yabai.window(window_ids[0]).warp(window_ids[1], insert_direction=append_direction)
    
    # Create the new split structure by warping windows in the opposite direction
    # We'll use the append direction to maintain the order
    for window_to_move in window_ids[1:]:
        # Warp the window to create a split in the new direction
        yabai.window(window_to_move).warp(target_window_id, insert_direction=append_direction)

        target_window_id = window_to_move

    from ..main import tree
    tree(pretty_print=True, nerd_font=True, space="focused")

def switch_split_command(window: str):
    """
    Switch the split direction of consecutive split siblings.
    
    This command finds all consecutive split siblings of the target window
    and recreates them as splits in the opposite axis direction, maintaining
    the same order of windows.
    """
    try:
        all_windows_data = yabai.query.windows(space="focused")
        if not all_windows_data:
            logging.error("[red]Error:[/red] No windows found in the current space.")
            raise typer.Exit(code=1)

        bsp_tree = reconstruct_tree(all_windows_data)
        if not bsp_tree:
            logging.error("[red]Error:[/red] Could not reconstruct BSP tree for the current space.")
            raise typer.Exit(code=1)

        target_window_data = yabai.query.window(window)
        if not target_window_data:
            logging.error(f"[red]Error:[/red] Could not find window: {window}")
            raise typer.Exit(code=1)
        target_window_id = target_window_data.id

        found_node = bsp_tree.find_window(target_window_id)

        if not found_node:
            logging.error(f"[red]Error:[/red] Window {target_window_id} not found in the BSP tree.")
            raise typer.Exit(code=1)

        _switch_split_direction(found_node)

    except YabaiError as e:
        logging.error(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1)