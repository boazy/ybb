import typer
import logging
from typing import List
from ..yabai import yabai, YabaiError
from ..tree import FindResult
from ..data_types import AdditionalInsertDirection, SplitType
from ..tree import reconstruct_tree, Split, Window, Stack, Node

def _get_all_windows_in_node(node: Node) -> List[int]:
    """Helper to get all window IDs from a node (Window, Stack, or Split)."""
    if isinstance(node, Window):
        return [node.id]
    elif isinstance(node, Stack):
        return [w.id for w in node.windows]
    elif isinstance(node, Split):
        windows = []
        if node.first_child:
            windows.extend(_get_all_windows_in_node(node.first_child))
        if node.second_child:
            windows.extend(_get_all_windows_in_node(node.second_child))
        return windows
    return []

def _handle_toggle_operation(found_node: FindResult):
    """
    Handle the toggle operation: if the window is in a stack, unroll it; otherwise, stack it.
    """

    # Check if our window is in a stack
    if found_node.parent_stack and len(found_node.parent_stack.windows) > 1:
        # Determine the split type of the parent split
        if len(found_node.ancestors) == 0:
            # Root stack, assume horizontal split
            target_split_type = SplitType.HORIZONTAL
        else:
            target_split_type = found_node.ancestors[-1].split_type

        # Unroll the stack
        _unroll_stack(found_node.parent_stack, target_split_type)
    else:
        # Stack together with all window in direct descendent and ancestor tree with the same split type
        _stack_recursive_splits(found_node)

def _contains_window(node: Node, window_id: int) -> bool:
    """Check if a node contains a specific window."""
    match node:
        case Window():
            return node.id == window_id
        case Stack():
            return any(w.id == window_id for w in node.windows)
        case Split():
            return (_contains_window(node.first_child, window_id) if node.first_child else False) or \
                (_contains_window(node.second_child, window_id) if node.second_child else False)
        case _:
            raise ValueError(f"Invalid node type: {type(node)}")

def _unroll_stack(stack: Stack, parent_split_type: SplitType):
    """
    Unroll a stack into a series of splits in the opposite direction of the parent split.
    """
    # We have nothing to do if the stack has only one window
    if len(stack.windows) <= 1:
        return
    
    # Determine the start direction and the append direction
    start_direction = parent_split_type.start_direction()
    append_direction = start_direction.opposite()
    
    # Get all window IDs in the stack
    window_ids = [w.id for w in stack.windows]

    # Start with the first window
    # Since we cannot warp a stacked window into a window in the same stack, we
    # first need to take out the first window out of the stack, and warp it on
    # top of the rest of the stack. We can then progressively unstack the rest
    # of the windows in its direction.
    # The most reliable trick for taking a window out of the stack and is to
    # toggle its floating state and then immediately toggle it back.
    # For more information, see: https://github.com/koekeishiya/yabai/issues/671

    base_window_id = window_ids[0]
    yabai.window(base_window_id).toggle("float")
    yabai.window(base_window_id).toggle("float")
    yabai.window(base_window_id).warp(window_ids[1], insert_direction=start_direction)

    previous_window_id = base_window_id

    for i in range(1, len(window_ids)):
        window_to_move = window_ids[i]
        
        # Now warp the stacked window to split the previous window
        yabai.window(window_to_move).warp(previous_window_id, insert_direction=append_direction)
        
        # Balance the ratios to make splits equal
        # ratio = 1.0 / (i + 1)
        #yabai.window(previous_window_id).ratio(ratio)

        previous_window_id = window_to_move

def _stack_recursive_splits(found_node: FindResult):
    """
    Recursively traverses the tree and performs stacking operations.
    This is a post-order traversal.
    """
    ancestors = found_node.ancestors

    if len(ancestors) == 0:
        logging.error("[red]Error:[/red] Cannot stack a window that is not part of a split (e.g., root window or root stack).")
        raise typer.Exit(code=1)

    direct_parent_split = ancestors[-1]
    target_split_type = direct_parent_split.split_type

    start_node = direct_parent_split
    for i in range(len(ancestors) - 2, -1, -1):
        potential_ancestor = ancestors[i]
        if potential_ancestor.split_type == target_split_type:
            start_node = potential_ancestor
        else:
            break

    windows_to_stack = []

    def _traverse(current_node: Node):
        if isinstance(current_node, Window):
            windows_to_stack.append(current_node.id)
            return

        if isinstance(current_node, Stack):
            for window in current_node.windows:
                windows_to_stack.append(window.id)
            return
        
        if not isinstance(current_node, Split) or current_node.split_type != target_split_type:
            return

        # Travel all the way down
        _traverse(current_node.first_child)
        _traverse(current_node.second_child)

    _traverse(start_node)

    if len(windows_to_stack) > 1:
        target_window_id = windows_to_stack[0]
        for current_id in windows_to_stack[1:]:
            yabai.window(current_id).warp(target_window_id, insert_direction=AdditionalInsertDirection.STACK)
            target_window_id = current_id
    
def stack_command(
    window: str = typer.Option("focused", "--window", "-w", help="Window to stack."),
    toggle: bool = typer.Option(False, "--toggle", help="Toggle between stacking and unstacking.")
):
    """
    Converts all the selected window's split siblings into a stack.
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

        if toggle:
            _handle_toggle_operation(found_node)
        else:
            _stack_recursive_splits(found_node)

    except YabaiError as e:
        logging.error(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1)
