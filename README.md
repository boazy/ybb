# YBB - Yabai BSP Builder

A powerful CLI tool that extends the [yabai](https://github.com/koekeishiya/yabai) window manager for macOS with
high-level commands for managing windows and spaces in a BSP (Binary Space Partitioning) layout.

## Features

- 🌳 **BSP Tree Visualization** - Reconstruct and visualize your window layout as a tree structure
- 📚 **Smart Window Stacking** - Automatically stack window siblings based on split orientation
- 🔄 **Split Direction Switching** - Switch the split direction of consecutive window siblings
- 🎯 **Intelligent Window Resizing** - Context-aware resizing that understands your BSP layout
- 🗑️ **Window Closing** - Close windows individually or close all other windows in a space
- 🎨 **Rich Console Output** - Beautiful colored output with automatic terminal detection
- 🔧 **Flexible Configuration** - Global options for verbosity and color control
- ⚡ **Fast and Lightweight** - Built with Python 3.13+ and modern tooling

## Installation

### Prerequisites

- macOS with [yabai](https://github.com/koekeishiya/yabai) installed and configured
- Python 3.13 or higher
- [uv](https://github.com/astral-sh/uv) package manager

### Install from source

```bash
git clone https://github.com/yourusername/ybb.git
cd ybb
uv sync
```

### Usage

YBB can be run directly with Python:

```bash
python -m ybb [OPTIONS] COMMAND [ARGS]...
```

## Commands

### Global Options

All commands support these global options:

- `--verbose`, `-V` - Enable verbose logging and debugging output
- `--color MODE` - Control color output mode (`always`, `auto`, `off`)

### Space Commands

#### `ybb space tree`

Reconstructs and displays the BSP tree structure of a space.

```bash
# Display BSP tree as JSON (default)
ybb space tree

# Display as a formatted tree with colors (pretty-print)
ybb space tree --pretty-print
ybb space tree -p

# Use Nerd Font icons for better visualization
ybb space tree -p --nerd-font
ybb space tree -p -N

# Target a specific space
ybb space tree --space 2 -p
```

**Example tree output:**

```tree
📱 Space 1 (bsp)
├─ 🪟 Terminal (1234)
└─ ┤ vertical
   ├─ 🪟 VS Code (5678)
   └─ 🪟 Safari (9012)
```

### Window Commands

#### `ybb window layout stack`

Converts window siblings into a stack based on their split orientation, or toggles between stacked and unstacked layouts.

```bash
# Stack siblings of the focused window
ybb window layout stack

# Stack siblings of a specific window
ybb window layout stack --window 1234

# Toggle between stacked and unstacked layout
ybb window layout stack --toggle

# Toggle for a specific window
ybb window layout stack --window 1234 --toggle
```

**Toggle Behavior:**
- If the window is part of a stack → unrolls the stack into balanced splits in the opposite direction
- If the window is not in a stack → stacks it with its siblings as normal

#### `ybb window layout switch-split`

Switches the split direction of consecutive split siblings. This command finds all windows that are split along the same axis and recreates them as splits in the opposite direction, maintaining the same order.

```bash
# Switch split direction for focused window's siblings
ybb window layout switch-split

# Switch split direction for specific window's siblings
ybb window layout switch-split --window 1234

# With verbose output to see the operation
ybb --verbose window layout switch-split
```

**How it works:**
- Finds all consecutive split siblings of the target window
- Determines current split direction (vertical/horizontal)
- Recreates the splits in the opposite direction
- Maintains the relative order of windows

**Example:** If you have 3 windows split vertically (side-by-side), this command will rearrange them to be split horizontally (stacked on top of each other).

#### `ybb window resize`

Intelligently resizes windows based on their position in the BSP tree.

```bash
# Expand the focused window by 50 pixels
ybb window resize 50

# Shrink the focused window by 50 pixels
ybb window resize -- -50

# Resize a specific window
ybb window resize 100 --window 1234

# Resize with verbose output to see the logic
ybb --verbose window resize 25
```

#### `ybb window close`

Closes windows individually or closes all other windows in the same space except the specified one.

```bash
# Close the focused window
ybb window close

# Close a specific window by ID
ybb window close --window 1234

# Close all other windows in the same space except the focused window
ybb window close --except

# Close all other windows in the same space except a specific window
ybb window close --window 1234 --except

# Close with verbose output to see the operation
ybb --verbose window close --except
```

**Exception Mode (`--except`):**
- Closes all windows in the same space as the target window
- Keeps the specified window open
- Useful for quickly decluttering a space while preserving your primary window
- Provides warnings if individual window close operations fail

#### `ybb window table`

Creates a comprehensive table layout of windows with detailed information and filtering options.

```bash
# Display table of all windows
ybb window table

# Display windows from a specific space (omits Space and Display columns)
ybb window table --space 1
ybb window table -s focused

# Display windows from a specific display (omits Display column)
ybb window table --display 1
ybb window table -d 2

# Display with verbose output
ybb --verbose window table

# Display with colors always on
ybb --color always window table
```

**Table Columns:**
- **Space** - Space ID and index in format "ID (INDEX)" (e.g., "27 (5)")
- **Display** - Display number
- **Id** - Window ID
- **App** - Application name (responsive width, minimum 10 characters)
- **Title** - Window title (responsive width, grows faster than App)
- **Layer** - Window layer (normal, above, below)
- **Sub-layer** - Window sub-layer
- **Flags** - 5-character status flags:
  - **R** - Root Window
  - **A** - Active (has focus)
  - **H/M/V** - Hidden, Minimized, or Visible (by priority)
  - **N/Z/z** - Native Fullscreen, Full Screen Zoom, or Parent Zoom
  - **F/S** - Floating or Sticky

**Filtering Options:**
- `--space` and `--display` are mutually exclusive
- When filtering by space, Space and Display columns are hidden
- When filtering by display, only Display column is hidden
- Column widths automatically adjust to terminal width
- Long text is truncated with ellipsis (…) when needed

**Example output:**
```
┏━━━━━━━━━━━━━┳━━━━┳━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━┳━━━━━━┓
┃       Space ┃ D… ┃     Id ┃ App         ┃ Title       ┃ Layer   ┃ Sub-lay… ┃ Fla… ┃
┡━━━━━━━━━━━━━╇━━━━╇━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━╇━━━━━━┩
│       1 (1) ┃  1 ┃  52018 ┃ WhatsApp    ┃ WhatsApp    ┃ normal  ┃ normal   ┃  R   ┃
│       2 (2) ┃  1 ┃     55 ┃ WezTerm     ┃ [4/4] ✳ YBB ┃ normal  ┃ below    ┃ RAV  ┃
│       3 (3) ┃  1 ┃     49 ┃ Firefox     ┃ GitHub      ┃ normal  ┃ below    ┃  R   ┃
└─────────────┴────┴────────┴─────────────┴─────────────┴─────────┴──────────┴──────┘
```

## Examples

### Basic Usage

```bash
# Quick tree visualization
ybb space tree -p -N

# Display window table
ybb window table

# Stack windows with verbose logging
ybb --verbose window layout stack

# Toggle stack/unstack with verbose output
ybb --verbose window layout stack --toggle

# Switch split direction with verbose output
ybb --verbose window layout switch-split

# Resize with colors always on (useful for scripts)
ybb --color always window resize 50

# Close all other windows except the focused one
ybb window close --except
```

### Advanced Workflows

```bash
# Debug a complex layout
ybb --verbose space tree -p -N

# Analyze windows in a specific space
ybb window table --space 1

# Monitor windows on a specific display
ybb window table --display 2

# Batch operations with color disabled
ybb --color off window layout stack
ybb --color off window layout switch-split
ybb --color off window resize 25
```

## How It Works

YBB works by:

1. **Querying yabai** for current window and space information
2. **Reconstructing the BSP tree** from window positions and sizes
3. **Analyzing relationships** between windows and their splits
4. **Executing intelligent operations** based on the tree structure

### BSP Tree Reconstruction

The tool reconstructs the binary space partitioning tree by:

- Analyzing window frames and positions
- Detecting split orientations (vertical/horizontal)
- Identifying stacked windows
- Building parent-child relationships

### Smart Resizing Logic

Window resizing is context-aware:

- **Vertical splits**: Adjusts left/right edges based on window position
- **Horizontal splits**: Adjusts top/bottom edges based on window position
- **Child position**: Determines which edge to move for intuitive behavior

### Stack Detection and Toggle

The stacking algorithm:

- Traverses the BSP tree to find split siblings
- Groups windows by their split orientation
- Executes yabai stack commands to create window stacks

**Toggle Mode:**
- Detects if a window is currently in a stack
- If stacked: Unrolls the stack into balanced splits in the opposite direction of the parent split
- If not stacked: Performs normal stacking operation

## Configuration

### Color Modes

- `always` - Force color output with truecolor support
- `auto` - Auto-detect terminal capabilities (default)
- `off` - Disable all color output

### Logging Levels

- Default: Shows errors and warnings
- `--verbose`: Shows debug information and command execution

## Development

### Setup

```bash
# Clone and setup development environment
git clone https://github.com/yourusername/ybb.git
cd ybb
uv sync
```

### Testing

```bash
# Run test suite
pytest tests/

# Test specific functionality
python -m ybb space tree
python -m ybb space tree -p
python -m ybb window table
python -m ybb window table -s 1
python -m ybb window layout stack
python -m ybb window layout switch-split
python -m ybb window resize 50
python -m ybb window close
python -m ybb window close --except
```

### Project Structure

```tree
ybb/
├── __init__.py          # Package initialization
├── __main__.py          # CLI entry point
├── main.py              # Command definitions and CLI setup
├── yabai.py             # Yabai integration and API wrapper
├── tree.py              # BSP tree reconstruction and algorithms
├── data_types.py        # Data structures for yabai objects
├── console.py           # Rich console integration
└── commands/
    ├── stack.py         # Window stacking functionality
    ├── switch_split.py  # Split direction switching
    ├── resize.py        # Smart window resizing
    ├── close.py         # Window closing functionality
    └── table.py         # Window table display
```

## Requirements

- **macOS** - Required for yabai compatibility
- **Python 3.13+** - Modern Python with latest features
- **yabai** - Window manager (must be installed and running)
- **Rich** - Terminal formatting and colors
- **Typer** - CLI framework

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Acknowledgments

- [yabai](https://github.com/koekeishiya/yabai) - The amazing window manager that makes this possible
- [Rich](https://github.com/Textualize/rich) - Beautiful terminal output
- [Typer](https://github.com/tiangolo/typer) - Modern CLI framework
