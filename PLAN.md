I want to create a CLI called `ybb` that automates some workflows with the
Tiling Window maanger for macOS _yabai_.

# Architecture

- The CLI is written in Python.
- Python 3.13 is the minimum supported version.
- We'll be using uv for version management.
- We try to be as DRY as possible!

## Modules

### yabai module

This is the yabai client.

- Define a low level function that wraps calling all yabai commands
`yabai.call`. It returns the stdout returned by Yabai or throws an exception if
yabai exits with an error.

- For every yabai command and feature we use wrap the low level function with a
  high levle function. For instances:
  - Query the sibling window: `yabai.query.windows(window = 'sibling')` 
  - Set the current space's layout to bsp: `yabai.space.layout('bsp')`
  - Set space 3's layout to float: `yabai.space.layout('float', space = 3)`.
- The high level interface is implemented to be as DRY as possible and follow
  the same structure as the Yabai CLI and naturally convert the high-level
  interface into cli commands.

## Tooling

- uv is used for version management.
- All dependencies are specified in pyproject.toml (do not use requirements.txt)
- mise-en-place (<https://mise.jdx.dev/configuration.html>) is used for python version management and for defining simple tasks

## Dependencies

- Typer is used for CLI

# Features

## CLI

The CLI has the following subcommands:

### ybb space

Space-specific commands

#### Keyword arguments

- `--space|-s=[focused|SPACE_SEL]`: Optional. Selects the target space using yabai's
  SPACE_SEL. If not specified, the focused space is selected.

### ybb space tree

#### Keyword arguments

- `--output-format|-o=FORMAT` Optional (default: `json`). Selects the target format.
  Options: `json` (self evident), `tree` shows a tree.
- `--nerd-font|-N` uses Nerd Font icons on the tree.

Reconstructs the BSP tree of the space and returns it as JSON.

### ybb window

Window-specific commands

#### Keyword arguments

- `--window|-w=[focused|WINDOW_SEL]`: Optional. Selects the target window using yabai's
  WINDOW_SEL. If not specified, the focused window is selected.

### ybb window layout stack

Layout is a subcommand of `ybb window` and `stack` is a subcommand of `ybb
window layout`.

Converts all the selected window's split siblings into a stack. With bsp layout,
this includes sibling's splits if the sibling's split follows the same axis as
the selected window's split.

For example, assuming the following layout:

```ascii
+-------------+
|       |     |
|       |  B  |
|       |     |
|   A   +-----+
|       |  C  |
|       +-----+
|       |  D  |
+-------+-----+
```

It does not necessarily follow from diagram, but in our case the BSP tree is:

```text
- (root) vertical-split
  |
  +-- (first sibling) A
  |
  +-- (second sibling) horizontal-split
      |
      +-- (first sibling) B
      |
      +-- (second sibling) horizontal-split
          |
          +-- (first sibling) C
          |
          +-- (second sibling) D
```

- A and B are siblings on a vertical split (A is the first child)
- B and C are siblings on a horizontal split (B is the first child of this pair)
- C and D are siblings on a horizontal split (C is the first child of this pair)

In this case, if we select A, B would be stacked into A, and if we select either
B, C or D, they would all be stacked together.

The algorithm for stacking is as follows:

1. Reconstruct the BSP tree by querying yabai.
2. Set start_node to the parent node of the current window.
3. Set target_split_type the split type of start_node.
4. If start_node is the root node, go to step 6.
5. Set parent_node to the parent_node of start_node.
6. If parent_node has the same split type as target_split_type set start_node to
   parent_node and go back to step 4.
7. Recursively all child nodes of start_node. If we encounter a child node that
   has a different split type from target_split_type, we stop the recursion. If
   we encounter the same target_split_type we stack the first sibling into the
   second sibling. We first travel all the way down before we start stacking up the
   tree.

### ybb window resize

This command performs a smart resize for a window. It receives one mandatory positional
argument which is the size increment. It can be in any of the following format:

- `{number}` (e.g. `50`): Increase size by number
- `+{number` (e.g. `+50`): Increase size by number
- `-{number}` (e.g. `-50`): Decrease size by number

This command works using the following algorithm:

1. If the window's split type is horizontal, we want to modify the _height_ of the
   window.
2. If the window's split type is vertical, we want to modify the _width_ of the
   window.
3. Automatically find the edge that will increase or decrease the window's size in the right direction (and do the inverse to the size of its sibling NODE in the bsp).
4. Call `yabai -m window --resize` to increase or decrease the with size on the correct axis and the correct edge.

