# VS Code Workspace Color Customizer

This script helps you manage unique color themes for your VS Code workspaces, making them easily distinguishable by their title bar and activity bar colors.

## Features

- **Workspace Discovery**: Automatically finds all workspaces in configured parent directories
- **Color Management**: 
  - Assigns unique color palettes to each workspace
  - Shows color previews in the terminal
  - Processes workspaces one at a time
  - Shows existing colors before suggesting changes
- **Interactive Workflow**:
  - Preview colors before applying
  - Accept (y), reject (n), or regenerate (r) colors for each workspace
  - Option to reset colors for any workspace
- **Configuration File**: Easy to edit `config.json` for managing:
  - Parent directories to scan for workspaces
  - Available color palettes with names and color codes
- **Special Modes**:
  - `--practice`: Preview changes without modifying any files
  - `--skip-existing`: Preserve existing workspace colors

## Setup

1. Create or edit `config.json` in the script directory:
   ```json
   {
       "parent_directories": [
           "~/prog",
           "~/other/projects"
       ],
       "colors": [
           {
               "name": "Green",
               "background": "#1d7823",
               "foreground": "#FFFFFF"
           },
           ...
       ]
   }
   ```

## Usage

1. **Basic Usage**:
   ```bash
   python workspace_color_customizer.py
   ```

2. **Practice Mode** (preview without changes):
   ```bash
   python workspace_color_customizer.py --practice
   ```

3. **Skip Existing Mode** (preserve existing colors):
   ```bash
   python workspace_color_customizer.py --skip-existing
   ```

## Workflow

1. The script shows all found workspaces and their current colors
2. For each workspace:
   - Shows current colors (if any)
   - Suggests a new color palette
   - You can:
     - Press `y` to accept the new colors
     - Press `n` to keep existing/no colors
     - Press `r` to generate a different color suggestion
3. After all workspaces, option to reset colors for any workspace

## Development

### Color Generation Algorithm

The script includes a sophisticated color generator (`color_generator.py`) that creates visually distinct colors:

- **Color Space**: Uses CIELAB color space for perceptually uniform color generation
- **Distinctness Measures**:
  - LAB Distance: Ensures colors are sufficiently different in perceptual space
  - Contrast Ratio: Maintains good contrast between colors and with text
- **Adaptive Requirements**:
  - Small sets (≤5 colors): Focuses on contrast between colors (minimum 1.5:1)
  - Medium sets (6-10 colors): Prioritizes text contrast (minimum 4.5:1)
  - Large sets (>10 colors): Optimizes for LAB space distribution
- **Features**:
  - Golden ratio-based hue distribution for even color spacing
  - Adaptive lightness and chroma for optimal contrast
  - Automatic foreground color selection (black/white)
  - RGB gamut checking for display-safe colors

### Running Tests

Run all tests with verbose output:
```bash
python -m unittest test_workspace_color_customizer.py -v
python -m unittest test_color_generator.py -v
```

## Notes

- Modifies `.vscode/settings.json` in each workspace
- Colors are applied to title bar and activity bar
- Each workspace gets a unique color to avoid confusion
- Backup your workspace settings before first use

## License

[MIT License]
