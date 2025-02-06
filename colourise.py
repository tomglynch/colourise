#!/usr/bin/env python3
import json
import os
import random
import sys
from color_generator import generate_distinct_colors

# Generate a larger set of distinct colors
def get_color_palette(num_colors=40):
    """Generate a palette of distinct colors."""
    color_pairs = generate_distinct_colors(num_colors)
    return [
        {
            "name": f"Color {i+1}",
            "background": bg.upper(),
            "foreground": fg
        }
        for i, (bg, fg) in enumerate(color_pairs)
    ]

# Global color palette - generated once when module is loaded
COLOURS = get_color_palette()

def get_random_colour():
    """Get a random colour from the palette."""
    return random.choice(COLOURS)

def show_colour_preview(bg_colour, fg_colour):
    """Show colour preview in terminal."""
    bg_rgb = tuple(int(bg_colour.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
    fg_rgb = tuple(int(fg_colour.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
    
    bg_ansi = f"\033[48;2;{bg_rgb[0]};{bg_rgb[1]};{bg_rgb[2]}m"
    fg_ansi = f"\033[38;2;{fg_rgb[0]};{fg_rgb[1]};{fg_rgb[2]}m"
    reset = "\033[0m"
    
    return f"{bg_ansi}{fg_ansi}  COLOUR PREVIEW  {reset}"

def get_user_choice():
    """Get user input for colour choice."""
    while True:
        choice = input("\nAccept this colour? (y)es/(r)egenerate/(n)o: ").lower()
        if choice in ['y', 'r', 'n']:
            return choice
        print("Invalid choice. Please enter 'y', 'r', or 'n'")

def apply_colour(colour, settings_path):
    """Apply the colour to settings file."""
    # Create .vscode directory if it doesn't exist
    os.makedirs(os.path.dirname(settings_path), exist_ok=True)

    # Load existing settings or create new
    try:
        with open(settings_path, 'r') as f:
            settings = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        settings = {}

    # Update colour customizations
    if 'workbench.colorCustomizations' not in settings:
        settings['workbench.colorCustomizations'] = {}

    new_colours = {
        "titleBar.activeBackground": colour['background'],
        "titleBar.activeForeground": colour['foreground'],
        "titleBar.inactiveBackground": colour['background'],
        "titleBar.inactiveForeground": colour['foreground'],
        "titleBar.border": colour['background'],
        "activityBar.background": colour['background'],
        "activityBar.foreground": colour['foreground']
    }

    settings['workbench.colorCustomizations'].update(new_colours)

    # Write settings
    with open(settings_path, 'w') as f:
        json.dump(settings, f, indent=4)

def colourise_workspace(practice_mode=False):
    """Add random colour to .vscode/settings.json in current directory."""
    settings_dir = os.path.join(os.getcwd(), '.vscode')
    settings_path = os.path.join(settings_dir, 'settings.json')

    while True:
        # Get random colour
        colour = get_random_colour()
        preview = show_colour_preview(colour['background'], colour['foreground'])
        
        print(f"\nSelected colour: {colour['name']}")
        print(f"Preview: {preview}")
        print(f"Background: {colour['background']}")
        print(f"Foreground: {colour['foreground']}")

        if practice_mode:
            print("\nPractice mode - no changes will be made")

        choice = get_user_choice()
        
        if choice == 'y':
            if not practice_mode:
                apply_colour(colour, settings_path)
                print(f"\nUpdated {settings_path}")
            else:
                print("\nPractice mode - would have updated settings")
            break
        elif choice == 'n':
            print("\nCancelled - no changes made")
            break
        else:  # choice == 'r'
            print("\nGenerating new colour...")
            continue

def show_all_colours():
    """Display all available colours."""
    print(f"\nTotal number of colours: {len(COLOURS)}\n")
    for colour in COLOURS:
        preview = show_colour_preview(colour['background'], colour['foreground'])
        print(f"{colour['name']}:")
        print(f"Preview: {preview}")
        print(f"Background: {colour['background']}")
        print(f"Foreground: {colour['foreground']}")
        print()

def main():
    if "--show-all" in sys.argv:
        show_all_colours()
    else:
        practice_mode = "--practice" in sys.argv
        colourise_workspace(practice_mode)

if __name__ == "__main__":
    main()