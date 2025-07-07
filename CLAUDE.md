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
    ├── resize.py          # Smart window resizing
    ├── close.py           # Window closing functionality
    └── table.py           # Window table display
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
   - Pretty-print option for convenient tree visualization
   - Nerd font icon support for tree visualization
   - Handles stacked windows properly

3. **Window Stacking** (`ybb window layout stack`)
   - Complete algorithm implementation
   - Tree traversal and stacking logic
   - Proper window selection and stacking execution
   - Toggle functionality for stacking/unstacking
   - Smart unroll logic that creates balanced splits in opposite direction
   - All data access patterns fixed

4. **Smart Resize** (`ybb window resize`)
   - Intelligent axis detection based on split type
   - Proper window selector handling
   - Dynamic resize amount calculation
   - Full yabai integration

5. **Window Close** (`ybb window close`)
   - Simple window closing functionality
   - Bulk close with --except option to close all other windows in the same space
   - Proper error handling for failed close operations
   - Full yabai integration

6. **Window Table** (`ybb window table`)
   - Comprehensive table display of all windows with Rich formatting
   - Responsive column sizing that adapts to terminal width
   - Space and display filtering with mutual exclusivity
   - 5-character flag system showing window status (R/A/H-M-V/N-Z-z/F-S)
   - Smart column visibility (hides irrelevant columns when filtering)
   - Enhanced yabai.query.windows() API with display parameter support

7. **Tree Management System**
   - Complete BSP tree data structures (Window, Stack, Split)
   - Tree traversal and window finding algorithms
   - Proper handling of vertical/horizontal splits
   - Stack detection and visualization

8. **Rich Console Integration**
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

- `ybb space tree [-s SPACE] [-o FORMAT] [-p] [-N]`: Reconstruct and display BSP tree
- `ybb window layout stack [-w WINDOW] [--toggle]`: Stack window siblings or toggle stack/unstack
- `ybb window resize INCREMENT [-w WINDOW]`: Smart window resize
- `ybb window close [-w WINDOW] [--except]`: Close window or all other windows in the same space
- `ybb window table [-d DISPLAY] [-s SPACE]`: Display comprehensive window table with filtering

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
- ✅ Window stacking operations with toggle functionality
- ✅ Smart window resizing
- ✅ Proper yabai integration
- ✅ Clean data access patterns
- ✅ Robust error handling
- ✅ Rich console integration with color support
- ✅ Comprehensive logging and debugging

## Usage Examples

```bash
# Display BSP tree for current space (JSON format)
ybb space tree

# Display tree in pretty-print format
ybb space tree --pretty-print
ybb space tree -p

# Display tree with nerd font icons and verbose logging
ybb --verbose space tree -p -N

# Display tree with colors forced on (useful for piping)
ybb --color always space tree -p

# Display comprehensive window table
ybb window table

# Display windows in a specific space (omits Space and Display columns)
ybb window table --space 1
ybb window table -s focused

# Display windows on a specific display (omits Display column)
ybb window table --display 1
ybb window table -d 2

# Stack siblings of focused window
ybb window layout stack

# Toggle between stacked and unstacked layout
ybb window layout stack --toggle

# Resize focused window by 50 pixels
ybb window resize 50

# Shrink focused window by 50 pixels
ybb window resize -- -50

# Resize specific window with verbose output
ybb --verbose window resize 100 -w 1234

# Disable colors entirely
ybb --color off space tree

# Close the focused window
ybb window close

# Close a specific window by ID
ybb window close -w 1234

# Close all windows in the same space except the focused window
ybb window close --except

# Close all windows in the same space except a specific window
ybb window close -w 1234 --except
```

## Test Commands

- `mise test` - Run test suite
- `python -m ybb space tree` - Display BSP tree (JSON format)
- `python -m ybb space tree -p` - Display BSP tree in pretty-print format
- `python -m ybb window table` - Display comprehensive window table
- `python -m ybb window table -s 1` - Display windows in space 1
- `python -m ybb window table -d 1` - Display windows on display 1
- `python -m ybb window layout stack` - Stack window siblings
- `python -m ybb window layout stack --toggle` - Toggle stack/unstack
- `python -m ybb window resize 50` - Resize focused window
- `python -m ybb window resize -- -50` - Shrink focused window
- `python -m ybb window close` - Close focused window
- `python -m ybb window close --except` - Close all other windows in the same space

## Lint and Unit Tests

Lint and testing is managed as mise tasks.

### Lint

Lint is using ruff.

- To run lints (check only) you should use `mise lint`.
- To auto fix lint issues you should use `mise lint:fix`.

### Tests

Tests are done using pytest

- To run tests, you should use `mise test`.

