import typer
import json
import logging
from enum import Enum
from rich.logging import RichHandler
from .yabai import WindowSelector, yabai, YabaiError
from .tree import reconstruct_tree, TreeEncoder, print_rich_tree
from .commands.stack import stack_command
from .commands.resize import resize_command
from .commands.switch_split import switch_split_command
from .console import ColorMode
from . import console

class OutputFormat(str, Enum):
    json = "json"
    tree = "tree"


app = typer.Typer()
space_app = typer.Typer()
window_app = typer.Typer()
app.add_typer(space_app, name="space")
app.add_typer(window_app, name="window")

@app.callback()
def main(
    verbose: bool = typer.Option(False, "--verbose", "-V", help="Enable verbose logging."),
    color: ColorMode = typer.Option(ColorMode.auto, "--color", help="Color output mode.")
):
    """YBB - A CLI tool for managing yabai windows and spaces."""
    # Initialize console with color mode
    console.initialize(color)
    
    # Configure logging based on verbose flag
    level = logging.WARNING
    if verbose:
        level = logging.DEBUG
    
    # Use the dedicated error console that respects color mode
    
    logging.basicConfig(
        level=level,
        format="%(message)s",
        handlers=[
            RichHandler(
                console=console.get().error,
                show_time=False,
                show_level=False,
                show_path=False,
                markup=True,
                rich_tracebacks=True,
                tracebacks_suppress=[typer]
            )
        ]
    )

layout_app = typer.Typer()
window_app.add_typer(layout_app, name="layout")

@layout_app.command(name="stack")
def _stack(
    window: str = typer.Option("focused", "--window", "-w", help="Window to stack.", metavar="WINDOW_SEL"),
    toggle: bool = typer.Option(False, "--toggle", help="Toggle between stacking and unstacking.")
):
    stack_command(window, toggle)

@layout_app.command(name="switch-split")
def _switch_split(
    window: str = typer.Option("focused", "--window", "-w", help="Window to switch split direction for.", metavar="WINDOW_SEL")
):
    switch_split_command(window)

@space_app.command()
def tree(
    space: str = typer.Option("focused", "--space", "-s", help="Space to reconstruct the tree for.", metavar="SPACE_SEL"),
    output_format: OutputFormat = typer.Option(OutputFormat.json, "--output-format", "-o", help="Output format (json or tree).", metavar="FORMAT"),
    nerd_font: bool = typer.Option(False, "--nerd-font", "-N", help="Use Nerd Font icons in tree output."),
    pretty_print: bool = typer.Option(False, "--pretty-print", "-p", help="Use tree format in output.")
):
    """
    Reconstructs the BSP tree of the space and returns it as JSON or a formatted tree.
    """
    try:
        windows = yabai.query.windows(space=space)
        spaces = yabai.query.spaces(space=space)

        if not spaces:
            logging.error(f"[red]Error:[/red] Space '{space}' not found.")
            raise typer.Exit(code=1)

        space_data = spaces[0]

        if space_data.type != 'bsp':
            logging.error(f"[red]Error:[/red] Space '{space}' is not a bsp space.")
            raise typer.Exit(code=1)

        if windows:
            tree_structure = reconstruct_tree(windows)
        else:
            tree_structure = None

        if pretty_print:
            output_format = OutputFormat.tree

        if output_format == OutputFormat.json:
            print(json.dumps(tree_structure, indent=2, cls=TreeEncoder))
        elif output_format == OutputFormat.tree:
            if not tree_structure:
                logging.warning(f"[red]Error:[/red] No windows found in space '{space}'.")
                return

            # Rich automatically handles color detection and falls back to plain text
            print_rich_tree(tree_structure, use_nerd_font=nerd_font)

    except YabaiError as e:
        logging.error(f"[red] Error:[/red] {e}")
        raise typer.Exit(code=1)

@window_app.command(name="resize")
def _resize(
    increment: int = typer.Argument(help="Amount to resize the window by (can be negative)."),
    window: str = typer.Option("focused", "--window", "-w", help="Window to resize.", metavar="WINDOW_SEL")
):
    resize_command(increment, window)

if __name__ == "__main__":
    app()
