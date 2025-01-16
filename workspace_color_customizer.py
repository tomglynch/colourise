import json
import os
import subprocess
import sys
import random

def get_existing_colors(workspace_dirs):
    """
    Extracts existing color customizations from workspaces.

    Args:
        workspace_dirs: List of directories containing workspaces.

    Returns:
        List of tuples containing existing color pairs.
    """
    existing_colors = []
    for workspace_dir in workspace_dirs:
        color = get_workspace_color(workspace_dir)
        if color:
            existing_colors.append(color)
    return existing_colors

def get_unused_colors(all_colors, existing_colors):
    """
    Finds colors that have not been used in existing workspaces.

    Args:
        all_colors: List of all available color tuples.
        existing_colors: List of existing color tuples.

    Returns:
        List of unused color tuples.
    """
    unused_colors = [color for color in all_colors if color not in existing_colors]
    return unused_colors

def hex_to_ansi_bg(hex_color):
    """
    Convert hex color to ANSI escape sequence for background.
    
    Args:
        hex_color: Hex color code (e.g., "#FF0000")
        
    Returns:
        ANSI escape sequence for the background color
    """
    # Remove the # if present
    hex_color = hex_color.lstrip('#')
    # Convert hex to RGB
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    # Return ANSI escape sequence
    return f"\033[48;2;{r};{g};{b}m"

def hex_to_ansi_fg(hex_color):
    """
    Convert hex color to ANSI escape sequence for foreground.
    
    Args:
        hex_color: Hex color code (e.g., "#FF0000")
        
    Returns:
        ANSI escape sequence for the foreground color
    """
    hex_color = hex_color.lstrip('#')
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return f"\033[38;2;{r};{g};{b}m"

def reset_color():
    """Returns ANSI escape sequence to reset colors."""
    return "\033[0m"

def show_color_preview(bg_color, fg_color):
    """
    Show a color preview in the terminal.
    
    Args:
        bg_color: Background color in hex
        fg_color: Foreground color in hex
    """
    bg_ansi = hex_to_ansi_bg(bg_color)
    fg_ansi = hex_to_ansi_fg(fg_color)
    reset = reset_color()
    preview = f"{bg_ansi}{fg_ansi}  COLOR PREVIEW  {reset}"
    return preview

def get_workspace_color(workspace_dir):
    """
    Get the current color customization for a workspace.
    
    Args:
        workspace_dir: Directory of the workspace.
        
    Returns:
        Tuple of (background_color, foreground_color) or None if no colors set.
    """
    # Check both possible locations for settings
    possible_paths = [
        os.path.join(workspace_dir, '.vscode', 'settings.json'),  # Workspace settings
        os.path.join(workspace_dir, 'settings.json'),            # Root settings
    ]
    
    for settings_path in possible_paths:
        try:
            with open(settings_path, 'r') as f:
                settings = json.load(f)
                if 'workbench.colorCustomizations' in settings:
                    customizations = settings['workbench.colorCustomizations']
                    if 'titleBar.activeBackground' in customizations:
                        return (
                            customizations['titleBar.activeBackground'],
                            customizations['titleBar.activeForeground']
                        )
        except (FileNotFoundError, json.JSONDecodeError):
            continue
    return None

def get_workspace_name(workspace_dir):
    """Get the name of the workspace from its path."""
    return os.path.basename(workspace_dir)

def print_header(text):
    """Print a formatted header."""
    print(f"\n{'='*80}")
    print(f" {text}")
    print(f"{'='*80}")

def print_section(text):
    """Print a formatted section header."""
    print(f"\n{'-'*40}")
    print(f" {text}")
    print(f"{'-'*40}")

def customize_workspace(workspace_dir, color_palette, practice_mode=False):
    """
    Customizes the workspace settings with the given color palette.

    Args:
        workspace_dir: Directory of the workspace.
        color_palette: Tuple of (background_color, foreground_color).
        practice_mode: If True, only simulate changes without writing them.
    """
    # Ensure .vscode directory exists
    vscode_dir = os.path.join(workspace_dir, '.vscode')
    os.makedirs(vscode_dir, exist_ok=True)
    settings_path = os.path.join(vscode_dir, 'settings.json')

    try:
        with open(settings_path, 'r') as f:
            settings = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        settings = {}

    if 'workbench.colorCustomizations' not in settings:
        settings['workbench.colorCustomizations'] = {}

    new_colors = {
        "titleBar.activeBackground": color_palette[0],
        "titleBar.activeForeground": color_palette[1],
        "titleBar.inactiveBackground": color_palette[0],
        "titleBar.inactiveForeground": color_palette[1],
        "titleBar.border": color_palette[0],
        "activityBar.background": color_palette[0],
        "activityBar.foreground": color_palette[1]
    }

    if not practice_mode:
        settings['workbench.colorCustomizations'].update(new_colors)
        with open(settings_path, 'w') as f:
            json.dump(settings, f, indent=4)

def confirm(prompt):
    """
    Asks the user for confirmation (y/n).

    Args:
        prompt: The question to ask the user.

    Returns:
        True if the user confirms, False otherwise.
    """
    while True:
        user_input = input(f"{prompt} (y/n): ").lower()
        if user_input == 'y':
            return True
        elif user_input == 'n':
            return False
        else:
            print("Invalid input. Please enter 'y' or 'n'.")

def reset_workspace_colors(workspace_dir, practice_mode=False):
    """
    Resets the color customizations for the given workspace.

    Args:
        workspace_dir: Directory of the workspace.
        practice_mode: If True, only simulate reset without actually doing it.
    """
    # Check both possible locations for settings
    possible_paths = [
        os.path.join(workspace_dir, '.vscode', 'settings.json'),  # Workspace settings
        os.path.join(workspace_dir, 'settings.json'),            # Root settings
    ]

    if practice_mode:
        print(f"\nWould reset colors for: {workspace_dir}")
        for path in possible_paths:
            print(f"Would remove 'workbench.colorCustomizations' from: {path}")
        return

    for settings_path in possible_paths:
        try:
            with open(settings_path, 'r') as f:
                settings = json.load(f)
                if 'workbench.colorCustomizations' in settings:
                    del settings['workbench.colorCustomizations']
                    with open(settings_path, 'w') as f:
                        json.dump(settings, f, indent=4)
        except FileNotFoundError:
            continue  # Try next path

def get_workspace_dirs(parent_dirs):
    """
    Get all subdirectories from the given parent directories.
    
    Args:
        parent_dirs: List of parent directory paths.
        
    Returns:
        List of workspace directory paths.
    """
    workspace_dirs = []
    for parent_dir in parent_dirs:
        parent_dir = os.path.expanduser(parent_dir)
        if os.path.exists(parent_dir):
            # Get immediate subdirectories only
            subdirs = [os.path.join(parent_dir, d) for d in os.listdir(parent_dir) 
                      if os.path.isdir(os.path.join(parent_dir, d))]
            workspace_dirs.extend(subdirs)
    return workspace_dirs

def get_random_unused_color(all_colors, used_colors):
    """
    Get a random color from the available colors that hasn't been used.
    
    Args:
        all_colors: List of all available color tuples.
        used_colors: List of color tuples already in use.
        
    Returns:
        A randomly selected unused color tuple.
    """
    available_colors = [color for color in all_colors if color not in used_colors]
    if not available_colors:
        return None
    return random.choice(available_colors)

def confirm_color(prompt):
    """
    Asks the user to accept, reject, or regenerate a color.

    Args:
        prompt: The question to ask the user.

    Returns:
        'y' for yes, 'n' for no, 'r' for regenerate
    """
    while True:
        user_input = input(f"{prompt} (y/n/r): ").lower()
        if user_input in ['y', 'n', 'r']:
            return user_input
        print("Invalid input. Please enter 'y' for yes, 'n' for no, or 'r' to regenerate color.")

def process_workspace(workspace, existing_color, all_colors, used_colors, practice_mode=False, skip_existing=False):
    """
    Process a single workspace, handling color assignment and user interaction.

    Args:
        workspace: The workspace directory to process.
        existing_color: Current color tuple if it exists, None otherwise.
        all_colors: List of all available color tuples.
        used_colors: Set of color tuples already in use.
        practice_mode: If True, only simulate changes.
        skip_existing: If True, don't modify workspaces with existing colors.

    Returns:
        The color tuple that was applied, or None if no change was made.
    """
    workspace_name = get_workspace_name(workspace)

    if existing_color:
        print(f"\nProcessing {workspace_name} (has existing colors):")
        current_preview = show_color_preview(existing_color[0], existing_color[1])
        print(f"Current: {current_preview} ({existing_color[0]}, {existing_color[1]})")
        
        if skip_existing:
            print("Skipping - already has colors")
            return None

    else:
        print(f"\nProcessing {workspace_name} (no existing colors):")

    while True:
        color_palette = get_random_unused_color(all_colors, used_colors)
        if not color_palette:
            print(f"\n❌ No more unique colors available for {workspace_name}")
            return None

        # Show the color change
        new_preview = show_color_preview(color_palette[0], color_palette[1])
        if existing_color:
            print(f"Suggested: {new_preview} ({color_palette[0]}, {color_palette[1]})")
        else:
            print(f"New: {new_preview} ({color_palette[0]}, {color_palette[1]})")

        if practice_mode:
            print(f"Practice mode - would write to {os.path.join(workspace, '.vscode', 'settings.json')}")

        response = confirm_color("Would you like these colors?")
        if response == 'y':
            if not practice_mode:
                used_colors.add(color_palette)
                customize_workspace(workspace, color_palette, practice_mode=False)
                print(f"Applied new colors to {workspace_name}")
            else:
                print(f"Practice mode - would apply new colors to {workspace_name}")
            return color_palette
        elif response == 'n':
            if existing_color:
                print(f"Keeping existing colors for {workspace_name}")
            else:
                print(f"Keeping workspace without colors")
            return None
        else:  # response == 'r'
            print("Generating new color...")
            continue

def load_config():
    """
    Load configuration from config.json file.
    
    Returns:
        Tuple of (parent_directories, color_tuples)
    """
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
            parent_dirs = config.get('parent_directories', [])
            colors = [(c['background'], c['foreground']) for c in config.get('colors', [])]
            return parent_dirs, colors
    except FileNotFoundError:
        print(f"\n❌ Config file not found at: {config_path}")
        print("Please create a config.json file with 'parent_directories' and 'colors' sections.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"\n❌ Error parsing config.json. Please ensure it is valid JSON.")
        sys.exit(1)
    except KeyError as e:
        print(f"\n❌ Missing required field in config.json: {e}")
        sys.exit(1)

def main(test_mode=False):
    # Load configuration from config file
    parent_dirs, all_colors = load_config()

    # Check command line arguments
    practice_mode = "--practice" in sys.argv
    skip_existing = "--skip-existing" in sys.argv
    
    print_header("VS Code Workspace Color Customizer")
    
    if practice_mode:
        print("\n🔍 Running in practice mode - no changes will be written")
    if skip_existing:
        print("\n⚡ Running in skip mode - existing colors will be preserved")

    # Get all workspace directories from parent directories
    workspace_dirs = get_workspace_dirs(parent_dirs)
    
    if not workspace_dirs:
        print("\n❌ No workspace directories found in the specified parent directories:")
        for dir in parent_dirs:
            print(f"  • {dir}")
        return

    # Get existing colors and show current state
    workspaces_with_colors = []
    workspaces_without_colors = []
    
    for workspace in workspace_dirs:
        existing_color = get_workspace_color(workspace)
        if existing_color:
            workspaces_with_colors.append((workspace, existing_color))
        else:
            workspaces_without_colors.append(workspace)

    print_section(f"Found {len(workspace_dirs)} workspaces")
    
    # Show workspaces with colors first
    if workspaces_with_colors:
        print("\nWorkspaces with existing colors:")
        for workspace, existing_color in workspaces_with_colors:
            workspace_name = get_workspace_name(workspace)
            color_preview = show_color_preview(existing_color[0], existing_color[1])
            print(f"• {workspace_name:25} {color_preview} ({existing_color[0]}, {existing_color[1]})")

    # Then show workspaces without colors
    if workspaces_without_colors:
        print("\nWorkspaces without colors:")
        for workspace in workspaces_without_colors:
            workspace_name = get_workspace_name(workspace)
            print(f"• {workspace_name:25} No colors")

    if not confirm("\nWould you like to proceed with color customization?"):
        return

    # Track colors that are in use (either existing or newly assigned)
    used_colors = set()
    
    # Add all existing colors to used_colors set
    for _, existing_color in workspaces_with_colors:
        used_colors.add(existing_color)

    print_section("Processing workspaces")

    # Process all workspaces in order (with colors first, then without)
    for workspace, existing_color in workspaces_with_colors:
        process_workspace(workspace, existing_color, all_colors, used_colors, practice_mode, skip_existing)

    for workspace in workspaces_without_colors:
        process_workspace(workspace, None, all_colors, used_colors, practice_mode, skip_existing)

    if confirm("\nDo you want to reset any workspaces back to no colors?"):
        print_section("Resetting colors")
        all_workspaces = [w for w, _ in workspaces_with_colors] + workspaces_without_colors
        for workspace in all_workspaces:
            workspace_name = get_workspace_name(workspace)
            if confirm(f"Reset colors for {workspace_name}? "):
                reset_workspace_colors(workspace, practice_mode)

if __name__ == "__main__":
    main(test_mode=False)