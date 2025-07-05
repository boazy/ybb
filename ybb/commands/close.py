import typer
import logging
from ..yabai import yabai, YabaiError


def close_command(
    window: str = "focused",
    except_mode: bool = False
):
    """
    Close a window or all windows except the specified one in the same space.
    
    Args:
        window: Window selector for the target window
        except_mode: If True, close all other windows in the same space except the target
    """
    try:
        # Get the target window
        target_window_data = yabai.query.window(window)
        if not target_window_data:
            logging.error(f"[red]Error:[/red] Could not find window: {window}")
            raise typer.Exit(code=1)
        
        target_window_id = target_window_data.id
        target_space_id = target_window_data.space

        if except_mode:
            # Get all windows in the same space as the target window
            all_windows_in_space = yabai.query.windows(space=target_space_id)
            
            # Filter out the target window to get windows to close
            windows_to_close = [w for w in all_windows_in_space if w.id != target_window_id]
            
            if not windows_to_close:
                logging.warning(f"[yellow]Warning:[/yellow] No other windows found in space {target_space_id} to close.")
                return
                
            logging.debug(f"[blue]Info:[/blue] Closing {len(windows_to_close)} windows in space {target_space_id}, keeping window {target_window_id}")
            
            # Close all other windows
            for window_to_close in windows_to_close:
                try:
                    yabai.window(window_to_close.id).close()
                    logging.debug(f"[green]Success:[/green] Closed window {window_to_close.id}")
                except YabaiError as e:
                    logging.warning(f"[yellow]Warning:[/yellow] Failed to close window {window_to_close.id}: {e}")
        else:
            # Simple close operation
            logging.debug(f"[blue]Info:[/blue] Closing window {target_window_id}")
            yabai.window(target_window_id).close()
            logging.debug(f"[green]Success:[/green] Closed window {target_window_id}")

    except YabaiError as e:
        logging.error(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1)