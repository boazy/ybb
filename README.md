# YBB - Yabai BSP Builder

A powerful CLI tool that extends the [yabai](https://github.com/koekeishiya/yabai) window manager for macOS with
high-level commands for managing windows and spaces in a BSP (Binary Space Partitioning) layout.

## Features

- 🌳 **BSP Tree Visualization** - Reconstruct and visualize your window layout as a tree structure
- 📚 **Smart Window Stacking** - Automatically stack window siblings based on split orientation
- 🎯 **Intelligent Window Resizing** - Context-aware resizing that understands your BSP layout
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

## Examples

### Basic Usage

```bash
# Quick tree visualization
ybb space tree -p -N

# Stack windows with verbose logging
ybb --verbose window layout stack

# Toggle stack/unstack with verbose output
ybb --verbose window layout stack --toggle

# Resize with colors always on (useful for scripts)
ybb --color always window resize 50
```

### Advanced Workflows

```bash
# Debug a complex layout
ybb --verbose space tree -p -N

# Batch operations with color disabled
ybb --color off window layout stack
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
python -m ybb window layout stack
python -m ybb window resize 50
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
    └── resize.py        # Smart window resizing
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
