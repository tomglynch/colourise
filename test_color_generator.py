import unittest
import random
from color_generator import (
    rgb_to_xyz, xyz_to_lab, lab_to_xyz, xyz_to_rgb,
    lab_distance, rgb_to_hex, generate_distinct_colors,
    get_contrast_ratio
)

class TestColorGenerator(unittest.TestCase):
    def setUp(self):
        random.seed(42)  # Set seed for reproducible tests

    def print_color_preview(self, colors, title):
        """Helper to print a visual preview of colors"""
        print(f"\n{'-'*20} {title} {'-'*20}")
        for i, (bg, fg) in enumerate(colors, 1):
            bg_ansi = f"\033[48;2;{int(bg[1:3], 16)};{int(bg[3:5], 16)};{int(bg[5:7], 16)}m"
            fg_ansi = f"\033[38;2;{int(fg[1:3], 16)};{int(fg[3:5], 16)};{int(fg[5:7], 16)}m"
            reset = "\033[0m"
            preview = f"{bg_ansi}{fg_ansi}  COLOR {i:02d}  {reset}"
            print(f"{preview} (bg: {bg}, fg: {fg})")

    def test_color_space_conversions(self):
        """Test color space conversion round trip"""
        # Test with a known RGB color (a shade of blue)
        r, g, b = 65, 105, 225  # Royal Blue
        
        # Convert RGB → XYZ → LAB → XYZ → RGB
        x, y, z = rgb_to_xyz(r, g, b)
        L, a, b_val = xyz_to_lab(x, y, z)
        x2, y2, z2 = lab_to_xyz(L, a, b_val)
        r2, g2, b2 = xyz_to_rgb(x2, y2, z2)

        # Allow small differences due to rounding
        self.assertAlmostEqual(r, r2, delta=1)
        self.assertAlmostEqual(g, g2, delta=1)
        self.assertAlmostEqual(b, b2, delta=1)

    def test_generate_small_set(self):
        """Test generating a small set of distinct colors"""
        n_colors = 5
        colors = generate_distinct_colors(n_colors)
        
        self.assertEqual(len(colors), n_colors)
        self.print_color_preview(colors, f"Small Set ({n_colors} colors)")

        # Test all pairs are sufficiently distinct
        for i, (bg1, _) in enumerate(colors):
            for bg2, _ in colors[i+1:]:
                contrast = get_contrast_ratio(bg1, bg2)
                self.assertGreater(contrast, 1.5, f"Colors too similar: {bg1} vs {bg2}")

    def test_generate_medium_set(self):
        """Test generating a medium set of distinct colors"""
        n_colors = 10
        colors = generate_distinct_colors(n_colors)
        
        self.assertEqual(len(colors), n_colors)
        self.print_color_preview(colors, f"Medium Set ({n_colors} colors)")

        # Verify foreground colors provide good contrast
        for bg, fg in colors:
            contrast = get_contrast_ratio(bg, fg)
            self.assertGreater(contrast, 4.5, f"Insufficient contrast: {bg} vs {fg}")

    def test_generate_large_set(self):
        """Test generating a large set of distinct colors"""
        n_colors = 20
        colors = generate_distinct_colors(n_colors)
        
        self.print_color_preview(colors, f"Large Set ({n_colors} colors)")
        
        # Count how many colors were actually generated
        print(f"\nGenerated {len(colors)} distinct colors out of {n_colors} requested")
        
        # Test minimum distance between colors in LAB space
        min_found_distance = float('inf')
        for i, (bg1, _) in enumerate(colors):
            for bg2, _ in colors[i+1:]:
                # Convert hex to RGB
                r1, g1, b1 = [int(bg1[i:i+2], 16) for i in (1, 3, 5)]
                r2, g2, b2 = [int(bg2[i:i+2], 16) for i in (1, 3, 5)]
                
                # Convert to LAB
                x1, y1, z1 = rgb_to_xyz(r1, g1, b1)
                x2, y2, z2 = rgb_to_xyz(r2, g2, b2)
                lab1 = xyz_to_lab(x1, y1, z1)
                lab2 = xyz_to_lab(x2, y2, z2)
                
                distance = lab_distance(lab1, lab2)
                min_found_distance = min(min_found_distance, distance)
        
        print(f"Minimum CIELAB distance between any two colors: {min_found_distance:.2f}")

    def test_contrast_ratios(self):
        """Test contrast ratios between colors"""
        colors = generate_distinct_colors(5)
        
        print("\n--- Contrast Ratio Matrix ---")
        print("     ", end="")
        for i, (bg, _) in enumerate(colors, 1):
            print(f"Color {i:02d}  ", end="")
        print()
        
        for i, (bg1, _) in enumerate(colors, 1):
            print(f"Color {i:02d}", end=" ")
            for bg2, _ in colors:
                ratio = get_contrast_ratio(bg1, bg2)
                print(f"{ratio:8.2f}", end="")
            print()

if __name__ == '__main__':
    unittest.main(verbosity=2) 