import json
import os
import unittest
from unittest.mock import patch, MagicMock

from workspace_color_customizer import (
    get_existing_colors, 
    get_unused_colors, 
    customize_workspace, 
    reset_workspace_colors,
    get_workspace_dirs,
    get_workspace_color,
    hex_to_ansi_bg,
    hex_to_ansi_fg,
    reset_color,
    show_color_preview,
    get_random_unused_color,
    load_config,
    main
)

class TestWorkspaceColorCustomizer(unittest.TestCase):

    def setUp(self):
        # Create a temporary directory structure for testing
        self.test_dir = "test_workspaces"
        os.makedirs(self.test_dir, exist_ok=True)

        # Create sample parent directories
        self.parent_dirs = [
            os.path.join(self.test_dir, "parent1"),
            os.path.join(self.test_dir, "parent2")
        ]
        
        # Create sample workspace directories in each parent
        self.workspace_dirs = []
        for parent in self.parent_dirs:
            os.makedirs(parent, exist_ok=True)
            workspace1 = os.path.join(parent, "workspace1")
            workspace2 = os.path.join(parent, "workspace2")
            os.makedirs(workspace1)
            os.makedirs(workspace2)
            self.workspace_dirs.extend([workspace1, workspace2])

        # Sample colors for testing
        self.test_colors = [
            ("#1d7823", "#FFFFFF"),  # Green
            ("#2196F3", "#FFFFFF"),  # Blue
            ("#F44336", "#FFFFFF"),  # Red
        ]

        # Create a test config file
        self.test_config = {
            "parent_directories": self.parent_dirs,
            "colors": [
                {"name": "Green", "background": "#1d7823", "foreground": "#FFFFFF"},
                {"name": "Blue", "background": "#2196F3", "foreground": "#FFFFFF"},
                {"name": "Red", "background": "#F44336", "foreground": "#FFFFFF"}
            ]
        }
        self.config_path = os.path.join(self.test_dir, "test_config.json")
        with open(self.config_path, 'w') as f:
            json.dump(self.test_config, f, indent=4)

    def tearDown(self):
        # Remove the temporary directory and all its contents
        import shutil
        shutil.rmtree(self.test_dir)

    def test_load_config(self):
        """Test loading configuration from file"""
        # Create mock config file
        config_path = os.path.join(self.test_dir, "config.json")
        with open(config_path, 'w') as f:
            json.dump(self.test_config, f, indent=4)

        # Mock the config file path
        with patch('os.path.abspath', return_value=os.path.join(self.test_dir, "workspace_color_customizer.py")):
            with patch('os.path.dirname', return_value=self.test_dir):
                parent_dirs, colors = load_config()
                self.assertEqual(parent_dirs, self.parent_dirs)
                self.assertEqual(colors, self.test_colors)

    def test_load_config_missing_file(self):
        """Test handling of missing config file"""
        nonexistent_dir = "/nonexistent"
        # Suppress stdout to avoid showing the error message during tests
        with open(os.devnull, 'w') as devnull:
            with patch('sys.stdout', new=devnull):
                with patch('os.path.abspath', return_value=os.path.join(nonexistent_dir, "workspace_color_customizer.py")):
                    with patch('os.path.dirname', return_value=nonexistent_dir):
                        with self.assertRaises(SystemExit):
                            load_config()

    def test_color_conversion_and_preview(self):
        """Test color conversion and preview functionality"""
        # Test hex to ANSI background conversion
        bg_ansi = hex_to_ansi_bg("#FF0000")
        self.assertEqual(bg_ansi, "\033[48;2;255;0;0m")

        # Test hex to ANSI foreground conversion
        fg_ansi = hex_to_ansi_fg("#00FF00")
        self.assertEqual(fg_ansi, "\033[38;2;0;255;0m")

        # Test color reset
        self.assertEqual(reset_color(), "\033[0m")

        # Test color preview generation
        preview = show_color_preview("#FF0000", "#FFFFFF")
        expected = "\033[48;2;255;0;0m\033[38;2;255;255;255m  COLOR PREVIEW  \033[0m"
        self.assertEqual(preview, expected)

    def test_workspace_color_management(self):
        """Test getting and setting workspace colors"""
        workspace_dir = self.workspace_dirs[0]
        vscode_dir = os.path.join(workspace_dir, '.vscode')
        os.makedirs(vscode_dir, exist_ok=True)

        # Test with no colors
        self.assertIsNone(get_workspace_color(workspace_dir))

        # Test setting colors
        color_palette = ("#1d7823", "#FFFFFF")
        customize_workspace(workspace_dir, color_palette, practice_mode=False)
        
        # Verify colors were set
        colors = get_workspace_color(workspace_dir)
        self.assertEqual(colors, color_palette)

        # Test resetting colors
        reset_workspace_colors(workspace_dir, practice_mode=False)
        self.assertIsNone(get_workspace_color(workspace_dir))

    def test_random_color_selection(self):
        """Test random color selection logic"""
        all_colors = self.test_colors
        
        # Test with no used colors
        used_colors = set()
        color = get_random_unused_color(all_colors, used_colors)
        self.assertIn(color, all_colors)
        
        # Test with some used colors
        used_colors = {self.test_colors[0]}
        for _ in range(5):  # Test multiple times due to randomness
            color = get_random_unused_color(all_colors, used_colors)
            self.assertIn(color, all_colors)
            self.assertNotIn(color, used_colors)
        
        # Test with all colors used
        used_colors = set(all_colors)
        color = get_random_unused_color(all_colors, used_colors)
        self.assertIsNone(color)

    def test_color_assignment_workflow(self):
        """Test the entire color assignment workflow"""
        workspace_dir = self.workspace_dirs[0]
        
        # Set up a workspace with existing colors
        existing_color = ("#1d7823", "#FFFFFF")
        customize_workspace(workspace_dir, existing_color, practice_mode=False)
        
        # Mock config loading
        with patch('workspace_color_customizer.load_config', return_value=(self.parent_dirs, self.test_colors)):
            # Mock user input to simulate workflow
            with patch('builtins.input', side_effect=['y', 'n', 'n', 'n']):  # proceed, reject color, skip reset for each workspace
                with patch('sys.argv', ['script.py']):  # Normal mode
                    with patch('builtins.print'):  # Suppress output
                        with patch('workspace_color_customizer.get_workspace_dirs', return_value=self.workspace_dirs[:1]):
                            main()
        
        # Verify original color was kept after rejecting new color
        current_color = get_workspace_color(workspace_dir)
        self.assertEqual(current_color, existing_color)

    def test_practice_mode(self):
        """Test practice mode doesn't modify files"""
        workspace_dir = self.workspace_dirs[0]
        
        # Set initial state
        initial_color = ("#1d7823", "#FFFFFF")
        customize_workspace(workspace_dir, initial_color, practice_mode=False)
        
        # Mock config loading
        with patch('workspace_color_customizer.load_config', return_value=(self.parent_dirs, self.test_colors)):
            # Run in practice mode
            with patch('builtins.input', side_effect=['y', 'y', 'n', 'n']):  # proceed, accept color, skip reset for each workspace
                with patch('sys.argv', ['script.py', '--practice']):
                    with patch('builtins.print'):
                        with patch('workspace_color_customizer.get_workspace_dirs', return_value=self.workspace_dirs[:1]):
                            main()
        
        # Verify colors weren't changed
        current_color = get_workspace_color(workspace_dir)
        self.assertEqual(current_color, initial_color)

    def test_skip_existing_mode(self):
        """Test skip-existing mode preserves existing colors"""
        workspace_dir = self.workspace_dirs[0]
        
        # Set initial state
        initial_color = ("#1d7823", "#FFFFFF")
        customize_workspace(workspace_dir, initial_color, practice_mode=False)
        
        # Mock config loading
        with patch('workspace_color_customizer.load_config', return_value=(self.parent_dirs, self.test_colors)):
            # Run in skip-existing mode
            with patch('builtins.input', side_effect=['y', 'n', 'n']):  # proceed, skip reset for each workspace
                with patch('sys.argv', ['script.py', '--skip-existing']):
                    with patch('builtins.print'):
                        with patch('workspace_color_customizer.get_workspace_dirs', return_value=self.workspace_dirs[:1]):
                            main()
        
        # Verify colors weren't changed
        current_color = get_workspace_color(workspace_dir)
        self.assertEqual(current_color, initial_color)

    def test_full_workflow_with_multiple_workspaces(self):
        """Test the full workflow with multiple workspaces"""
        # Set up initial states
        workspace1 = self.workspace_dirs[0]
        workspace2 = self.workspace_dirs[1]
        
        # Give workspace1 an initial color
        initial_color = ("#1d7823", "#FFFFFF")
        customize_workspace(workspace1, initial_color, practice_mode=False)
        
        # Mock config loading
        with patch('workspace_color_customizer.load_config', return_value=(self.parent_dirs, self.test_colors)):
            # Run workflow:
            # 1. Yes to proceed
            # 2. No to changing workspace1's color
            # 3. Yes to new color for workspace2
            # 4. No to resetting colors for each workspace
            with patch('builtins.input', side_effect=['y', 'n', 'y', 'n', 'n']):
                with patch('sys.argv', ['script.py']):
                    with patch('builtins.print'):
                        with patch('workspace_color_customizer.get_workspace_dirs', return_value=self.workspace_dirs[:2]):
                            main()
        
        # Verify workspace1 kept its color
        color1 = get_workspace_color(workspace1)
        self.assertEqual(color1, initial_color)
        
        # Verify workspace2 got a color
        color2 = get_workspace_color(workspace2)
        self.assertIsNotNone(color2)
        self.assertNotEqual(color2, initial_color)  # Should be different from workspace1's color

    def test_regenerate_color_option(self):
        """Test the regenerate color option"""
        workspace_dir = self.workspace_dirs[0]
        
        # Mock config loading
        with patch('workspace_color_customizer.load_config', return_value=(self.parent_dirs, self.test_colors)):
            # Run workflow with regenerate option:
            # 1. Yes to proceed
            # 2. Regenerate color
            # 3. Accept new color
            # 4. No to resetting
            with patch('builtins.input', side_effect=['y', 'r', 'y', 'n']):
                with patch('sys.argv', ['script.py']):
                    with patch('builtins.print'):
                        with patch('workspace_color_customizer.get_workspace_dirs', return_value=self.workspace_dirs[:1]):
                            main()
        
        # Verify workspace got a color
        color = get_workspace_color(workspace_dir)
        self.assertIsNotNone(color)
        self.assertIn(color, self.test_colors)

if __name__ == '__main__':
    unittest.main()