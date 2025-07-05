from __future__ import annotations
from dataclasses import dataclass
import re
from typing import List, Optional, Union, Dict, Any
import json

from rich.text import Text
from rich.tree import Tree as RichTree
from ybb.data_types import Frame, Window as RawWindow, SplitType
from ybb import console

@dataclass(frozen=True)
class WindowContext:
    window: Window
    tree: Node
    ancestors: List[Split]
    is_first_child: bool
    parent_stack: Optional[Stack] = None

    def consecutive_split_siblings(self) -> List[Window]:
        """
        Returns all the windows that are split along the same axis and have the same dimensions on the split axis as the current window.
        This function conceptually reanalyzes the BSP layout as a tree of splits with flexible number of children for each split.
        For example, given the BSP tree below:
        HSplit(
            VSplit(
                VSplit(
                    Window(1),
                    Window(2),
                ),
                VSplit(
                    Window(3),
                    HSplit(
                        Window(4),
                        Window(5),
                    ),
                ),
            ),
            Window(6),
        )
        And starting at window 3, the function should return windows [1, 2, 3].
        Windows 4 and 5 are split on a different axis and do not share the same
        dimensions. Window 6 is on the same axis and share the same dimensions,
        but it is separated from windows [1, 2, 3] by the opposite split that
        contains windows [4, 5], so it is not considered a consecutive sibling.
        """
        if self.parent_stack and len(self.parent_stack.windows) > 1:
            return self.parent_stack.windows

        ancestors = self.ancestors
        if not ancestors:
            # If the window has no ancestors, the window is the root window.
            # The root window has no split siblings.
            return [self.window]

        direct_parent_split = ancestors[-1]
        our_split_type = direct_parent_split.split_type

        # Find the furthest ancestor that has the same (consecutive)split type as the direct parent split.
        start_node = direct_parent_split
        for potential_ancestor in reversed(ancestors[:-1]):
            if potential_ancestor.split_type == our_split_type:
                start_node = potential_ancestor
            else:
                break

        consecutive_siblings: List[Window] = []
        consecutive_siblings_groups = [consecutive_siblings]

        def _traverse(current_node: Node):
            nonlocal consecutive_siblings
            match current_node:
                case Window():
                    consecutive_siblings.append(current_node)
                case Stack():
                    consecutive_siblings.extend(current_node.windows)
                case Split(split_type=split_type):
                    if split_type == our_split_type:
                        _traverse(current_node.first_child)
                        _traverse(current_node.second_child)
                    else:
                        # If the split type does not match, we have a break. Any
                        # siblings that are found later are non-consecutive, and
                        # must be counted in another group, so we create a new group
                        # instead of the current one.
                        consecutive_siblings = []
                        consecutive_siblings_groups.append(consecutive_siblings)

                case _:
                    raise ValueError(f"Unknown node type: {type(current_node)}")

        _traverse(start_node)

        # Short circuit if there is only one group.
        if len(consecutive_siblings_groups) == 1:
            return consecutive_siblings_groups[0]

        return next((x for x in consecutive_siblings_groups if self.window in x), [self.window])

@dataclass(frozen=True)
class Window:
    id: int
    app: str
    title: str
    frame: Frame
    is_leaf: bool = True

    @staticmethod
    def from_raw(raw: RawWindow) -> Window:
        return Window(
            id=raw.id,
            app=raw.app,
            title=raw.title,
            frame=raw.frame
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "app": self.app,
            "title": self.title,
            "frame": self.frame.__dict__,
            "is_leaf": self.is_leaf,
            "type": "window"
        }

    def find_window(self, window_id: int) -> Optional[WindowContext]:
        return self._find_window(self, window_id, [], False)
    
    def _find_window(self, tree: Node, window_id: int, ancestors: List['Split'], is_first_child: bool) -> Optional[WindowContext]: # type: ignore
        if self.id == window_id:
            return WindowContext(self, tree, ancestors, is_first_child)
        return None

@dataclass(frozen=True)
class Stack:
    windows: List[Window]
    frame: Frame
    is_leaf: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "windows": [w.to_dict() for w in self.windows],
            "frame": self.frame.__dict__,
            "is_leaf": self.is_leaf,
            "type": "stack"
        }

    def find_window(self, window_id: int) -> Optional[WindowContext]:
        return self._find_window(self, window_id, [], False)

    def _find_window(self, tree: Node, window_id: int, ancestors: List['Split'], is_first_child: bool) -> Optional[WindowContext]:
        for window in self.windows:
            if window.id == window_id:
                return WindowContext(window, tree, ancestors, is_first_child, parent_stack=self)
        return None

@dataclass(frozen=True)
class Split:
    first_child: 'Node'
    second_child: 'Node'
    split_type: SplitType
    frame: Frame
    is_leaf: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "first_child": self.first_child.to_dict(),
            "second_child": self.second_child.to_dict(),
            "split_type": self.split_type.value,
            "frame": self.frame.__dict__,
            "is_leaf": self.is_leaf,
            "type": "split"
        }

    def find_window(self, window_id: int) -> Optional[WindowContext]:
        return self._find_window(self, window_id, [], False)

    def _find_window(self, tree: Node, window_id: int, ancestors: List['Split'], is_first_child: bool) -> Optional[WindowContext]:
        ancestors.append(self)
        result = self.first_child._find_window(tree, window_id, ancestors, True)
        if result:
            return result
        result = self.second_child._find_window(tree, window_id, ancestors, False)
        if result:
            return result
        ancestors.pop()
        return None

class TreeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, (Window, Stack, Split)):
            return o.to_dict()
        if isinstance(o, Frame):
            return o.__dict__
        if isinstance(o, SplitType):
            return o.value
        return super().default(o)


def _create_frame_from_windows(windows: List[RawWindow]) -> Frame:
    if not windows:
        return Frame(0, 0, 0, 0)
    min_x = min(w.frame.left for w in windows)
    min_y = min(w.frame.top for w in windows)
    max_r = max(w.frame.right for w in windows)
    max_b = max(w.frame.bottom for w in windows)
    return Frame(x=min_x, y=min_y, w=max_r - min_x, h=max_b - min_y)

def _find_best_split(windows: List[RawWindow]) -> Optional[tuple[SplitType, float]]:
    """Find the best split line (vertical or horizontal) for a group of windows."""
    vertical_candidates = set()
    horizontal_candidates = set()

    for w in windows:
        vertical_candidates.add(w.frame.left)
        vertical_candidates.add(w.frame.right)
        horizontal_candidates.add(w.frame.top)
        horizontal_candidates.add(w.frame.bottom)

    best_split = None
    max_spread = -1

    # Check vertical splits
    for x in sorted(list(vertical_candidates)):
        left = [w for w in windows if w.frame.right <= x + 0.1]
        right = [w for w in windows if w.frame.left >= x - 0.1]
        if left and right and len(left) + len(right) == len(windows):
            # This is a clean split
            spread = abs(_create_frame_from_windows(left).center_x - _create_frame_from_windows(right).center_x)
            if spread > max_spread:
                max_spread = spread
                best_split = (SplitType.VERTICAL, x)

    # Check horizontal splits
    for y in sorted(list(horizontal_candidates)):
        top = [w for w in windows if w.frame.bottom <= y + 0.1]
        bottom = [w for w in windows if w.frame.top >= y - 0.1]
        if top and bottom and len(top) + len(bottom) == len(windows):
            spread = abs(_create_frame_from_windows(top).center_y - _create_frame_from_windows(bottom).center_y)
            if spread > max_spread:
                max_spread = spread
                best_split = (SplitType.HORIZONTAL, y)

    return best_split

def _build_tree_recursive(windows: List[RawWindow]) -> Node:
    if len(windows) < 1:
        raise ValueError("windows list must not be empty")

    first_window = windows[0]
    # Check for a stack (all windows have the same frame)
    first_frame = first_window.frame
    if all(w.frame == first_frame for w in windows):
        sorted_wins = sorted(windows, key=lambda w: w.stack_index or 0)
        return Stack(
            windows=[Window.from_raw(w) for w in sorted_wins],
            frame=first_frame
        )

    if len(windows) == 1:
        return Window.from_raw(first_window)

    split = _find_best_split(windows)
    if not split:
        # Cannot split, treat as a stack (fallback)
        sorted_wins = sorted(windows, key=lambda w: w.stack_index or w.id)
        return Stack(
            windows=[Window.from_raw(w) for w in sorted_wins],
            frame=_create_frame_from_windows(windows)
        )

    split_type, line = split
    if split_type == SplitType.VERTICAL:
        left_wins = [w for w in windows if w.frame.right <= line + 0.1]
        right_wins = [w for w in windows if w.frame.left >= line - 0.1]
        first_child = _build_tree_recursive(left_wins)
        second_child = _build_tree_recursive(right_wins)
    else: # HORIZONTAL
        top_wins = [w for w in windows if w.frame.bottom <= line + 0.1]
        bottom_wins = [w for w in windows if w.frame.top >= line - 0.1]
        first_child = _build_tree_recursive(top_wins)
        second_child = _build_tree_recursive(bottom_wins)

    return Split(
        first_child=first_child,
        second_child=second_child,
        split_type=split_type,
        frame=_create_frame_from_windows(windows)
    )


def reconstruct_tree(windows: List[RawWindow]) -> Node:
    """Reconstructs the BSP tree from a flat list of window data."""
    return _build_tree_recursive(windows)


NERD_FONT_ICONS = {
    SplitType.VERTICAL: "\ueb56",
    SplitType.HORIZONTAL: "\ueb57",
    "stack": "\uf51e",
    "window": "\ueb7f",
}


def _format_node_label(node: Node, use_nerd_font: bool) -> str:
    if isinstance(node, Window):
        icon = f"{NERD_FONT_ICONS['window']} " if use_nerd_font else ""
        return f"{icon}{node.app}: {node.title} ({node.id})"
    if isinstance(node, Stack):
        icon = NERD_FONT_ICONS["stack"] if use_nerd_font else "stack"
        return f"{icon} ({len(node.windows)} windows)"
    if isinstance(node, Split):
        icon = NERD_FONT_ICONS[node.split_type] if use_nerd_font else node.split_type.value
        return f"{icon}"


def format_tree(tree: Node, use_nerd_font: bool = False) -> str:
    """Formats the reconstructed tree into a human-readable string."""

    def _recurse(node: Node, prefix: str = "", is_last: bool = True) -> list[str]:
        # If the node is a stack with a single window, just format the window directly.
        if isinstance(node, Stack) and len(node.windows) == 1:
            return _recurse(node.windows[0], prefix, is_last)

        lines = []
        connector = "└── " if is_last else "├── "
        lines.append(f"{prefix}{connector}{_format_node_label(node, use_nerd_font)}")

        new_prefix = prefix + ("    " if is_last else "│   ")

        children_to_render = []
        if isinstance(node, Split):
            children_to_render = [node.first_child, node.second_child]
        elif isinstance(node, Stack):
            children_to_render = node.windows

        for i, child in enumerate(children_to_render):
            is_child_last = (i == len(children_to_render) - 1)
            lines.extend(_recurse(child, new_prefix, is_child_last))

        return lines


    # If the root is a stack with a single window, unwrap it.
    if isinstance(tree, Stack) and len(tree.windows) == 1:
        tree = tree.windows[0]

    lines = [_format_node_label(tree, use_nerd_font)]

    children_to_render = []
    if isinstance(tree, Split):
        children_to_render = [tree.first_child, tree.second_child]
    elif isinstance(tree, Stack):
         children_to_render = tree.windows

    for i, child in enumerate(children_to_render):
        is_last_child = (i == len(children_to_render) - 1)
        lines.extend(_recurse(child, "", is_last_child))

    return "\n".join(lines)


def _create_rich_node_label(node: Node, use_nerd_font: bool) -> Text:
    """Create a Rich Text object with colors for a node."""
    match node:
        case Window(app=app, title=title, id=id):
            text = Text()
            if use_nerd_font:
                text.append(f"{NERD_FONT_ICONS['window']} ", style="bright_blue")
            text.append(f"{app}", style="bright_green bold")
            text.append(": ", style="dim")
            text.append(f"{title}", style="white")
            text.append(f" ({id})", style="bright_black")
            return text
        case Stack(windows=windows):
            text = Text()
            if use_nerd_font:
                text.append(f"{NERD_FONT_ICONS['stack']} ", style="bright_yellow")
            text.append(f"({len(windows)} windows)", style="bright_magenta")
            return text
        case Split(split_type=split_type):
            text = Text()
            if use_nerd_font:
                icon = NERD_FONT_ICONS[split_type]
                style = "bright_cyan" if split_type == SplitType.VERTICAL else "bright_red"
                text.append(f"{icon}", style=style)
            else:
                text.append(split_type.value, style="bright_cyan" if split_type == SplitType.VERTICAL else "bright_red")
            return text
        case _:
            return Text("unknown", style="red")

def print_rich_tree(tree: Node, use_nerd_font: bool = False) -> None:
    """Formats the reconstructed tree into a Rich-colored string."""

    def _render_child(node: Node, tree: RichTree) -> RichTree:
        label = _create_rich_node_label(node, use_nerd_font)
        return tree.add(label)

    def _recurse(node: Node, tree: RichTree) -> None:
        """Recursively build a Rich tree structure."""
        children_to_render = []
        if isinstance(node, Split):
            children_to_render = [node.first_child, node.second_child]
        elif isinstance(node, Stack):
            children_to_render = node.windows
        
        for child in children_to_render:
            if isinstance(child, Stack) and len(child.windows) == 1:
                # If the child node is a stack with a single window, just render the window directly.
                _render_child(child.windows[0], tree)
            else:
                _recurse(child, _render_child(child, tree)) # type: ignore

    # If the root is a stack with a single window, unwrap it.
    if isinstance(tree, Stack) and len(tree.windows) == 1:
        tree = tree.windows[0]
    
    root_label = _create_rich_node_label(tree, use_nerd_font)
    rich_tree = RichTree(root_label)
    
    children_to_render = []
    if isinstance(tree, Split):
        children_to_render = [tree.first_child, tree.second_child]
    elif isinstance(tree, Stack):
        children_to_render = tree.windows
    
    for child in children_to_render:
        child_label = _create_rich_node_label(child, use_nerd_font)
        child_tree = rich_tree.add(child_label)
        _recurse(child, child_tree)
    
    # Capture the Rich output as a string
    console.get().main.print(rich_tree)


Node = Union[Window, Stack, Split]

