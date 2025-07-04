import typer
import sys
import logging
from typing import List
from ..yabai import yabai, YabaiError
from ..tree import SplitType
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

def _stack_recursive_traversal(current_node: Node, target_split_type: SplitType):
    """
    Recursively traverses the tree and performs stacking operations.
    This is a post-order traversal.
    """
    if not current_node:
        return

    if isinstance(current_node, Split):
        # Travel all the way down
        _stack_recursive_traversal(current_node.first_child, target_split_type)
        _stack_recursive_traversal(current_node.second_child, target_split_type)

        # Now, on the way up, perform stacking if the split type matches
        if current_node.split_type == target_split_type:
            # Stack the first child into the second child
            # This assumes first_child and second_child are windows or stacks
            # If they are splits, we need to get their contained windows/stacks
            windows_from_first_child = _get_all_windows_in_node(current_node.first_child)

            target_window_id = None
            if current_node.second_child:
                all_windows_in_second_child = _get_all_windows_in_node(current_node.second_child)
                if all_windows_in_second_child:
                    target_window_id = all_windows_in_second_child[0] # Stack into the first window found

            if target_window_id and windows_from_first_child:
                for win_id in windows_from_first_child:
                    if win_id != target_window_id: # Don't stack a window onto itself
                        yabai.window(target_window_id).stack(win_id)

def stack_command(
    window: str = typer.Option("focused", "--window", "-w", help="Window to stack.")
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

        _stack_recursive_traversal(start_node, target_split_type)

    except YabaiError as e:
        logging.error(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1)
