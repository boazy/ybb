# YBB CLI Project State

## Overview

YBB is a CLI tool that extends the yabai window manager for macOS. It provides
high-level commands for managing windows and spaces in a BSP (Binary Space
Partitioning) layout.

## Architecture

- **Language**: Python 3.13+
- **CLI Framework**: Typer
- **Package Manager**: uv
- **Dependencies**: typer, rich, dataclasses-json

## Project Structure

```text
ybb/
├── __init__.py
├── __main__.py
├── main.py                 # CLI entry point and command definitions
├── yabai.py               # Yabai client wrapper
├── tree.py                # BSP tree reconstruction and management
├── data_types.py          # Data structures for yabai objects
└── commands/
    ├── stack.py           # Window stacking functionality
    └── resize.py          # Smart window resizing
```

## Current Implementation Status

### ✅ Fully Working Features

1. **Core Infrastructure**
   - `yabai.py`: Low-level yabai command wrapper with high-level API
   - `data_types.py`: Complete data structures for Window, Space, and Frame
   - `tree.py`: BSP tree reconstruction algorithm
   - Project setup with uv and proper dependencies

2. **Space Tree Command** (`ybb space tree`)
   - Reconstructs BSP tree from window layout
   - Supports JSON and tree output formats
   - Nerd font icon support for tree visualization
   - Handles stacked windows properly

3. **Window Stacking** (`ybb window layout stack`)
   - Complete algorithm implementation
   - Tree traversal and stacking logic
   - Proper window selection and stacking execution
   - All data access patterns fixed

4. **Smart Resize** (`ybb window resize`)
   - Intelligent axis detection based on split type
   - Proper window selector handling
   - Dynamic resize amount calculation
   - Full yabai integration

5. **Tree Management System**
   - Complete BSP tree data structures (Window, Stack, Split)
   - Tree traversal and window finding algorithms
   - Proper handling of vertical/horizontal splits
   - Stack detection and visualization

6. **Rich Console Integration**
   - Colored output with automatic terminal detection
   - Truecolor support for enhanced visuals
   - Verbose logging with Rich formatting
   - Graceful fallback for non-color terminals

## Command Interface

### Global Options

All commands support these global options:

- `--verbose`, `-V`: Enable verbose logging and debugging output
- `--color MODE`: Control color output mode
  - `always`: Force color output with truecolor support
  - `auto`: Auto-detect terminal capabilities (default)
  - `off`: Disable all color output

### Available Commands

- `ybb space tree [-s SPACE] [-o FORMAT] [-N]`: Reconstruct and display BSP tree
- `ybb window layout stack [-w WINDOW]`: Stack window siblings
- `ybb window resize INCREMENT [-w WINDOW]`: Smart window resize

### Command Architecture

- Main CLI in `main.py` with Typer sub-applications
- Commands delegate to separate modules in `commands/`
- Consistent error handling with YabaiError exceptions
- Rich console integration for enhanced output formatting

## Development Environment

- **Python**: 3.13+ (managed by mise)
- **Package Manager**: uv
- **Testing**: pytest (basic tests in `tests/test_tree.py`)
- **Configuration**: pyproject.toml for dependencies

## Project Status

The YBB CLI tool is **fully functional** with all core features working correctly:

- ✅ BSP tree reconstruction and visualization
- ✅ Window stacking operations
- ✅ Smart window resizing
- ✅ Proper yabai integration
- ✅ Clean data access patterns
- ✅ Robust error handling
- ✅ Rich console integration with color support
- ✅ Comprehensive logging and debugging

## Usage Examples

```bash
# Display BSP tree for current space
ybb space tree

# Display tree with nerd font icons and verbose logging
ybb --verbose space tree -N

# Display tree with colors forced on (useful for piping)
ybb --color always space tree

# Stack siblings of focused window
ybb window layout stack

# Resize focused window by 50 pixels
ybb window resize 50

# Shrink focused window by 50 pixels
ybb window resize -- -50

# Resize specific window with verbose output
ybb --verbose window resize 100 -w 1234

# Disable colors entirely
ybb --color off space tree
```

## Test Commands

- `pytest tests/` - Run test suite
- `python -m ybb space tree` - Display BSP tree
- `python -m ybb window layout stack` - Stack window siblings
- `python -m ybb window resize 50` - Resize focused window
- `python -m ybb window resize -- -50` - Shrink focused window
