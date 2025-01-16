import math
import random

def rgb_to_xyz(r, g, b):
    """Convert RGB color space to XYZ color space."""
    r = r / 255
    g = g / 255
    b = b / 255

    # Convert to linear RGB
    r = ((r + 0.055) / 1.055) ** 2.4 if r > 0.04045 else r / 12.92
    g = ((g + 0.055) / 1.055) ** 2.4 if g > 0.04045 else g / 12.92
    b = ((b + 0.055) / 1.055) ** 2.4 if b > 0.04045 else b / 12.92

    # Convert to XYZ
    x = r * 0.4124564 + g * 0.3575761 + b * 0.1804375
    y = r * 0.2126729 + g * 0.7151522 + b * 0.0721750
    z = r * 0.0193339 + g * 0.1191920 + b * 0.9503041

    return x * 100, y * 100, z * 100

def xyz_to_lab(x, y, z):
    """Convert XYZ color space to LAB color space."""
    # D65 illuminant reference values
    xn, yn, zn = 95.047, 100.0, 108.883

    x = x / xn
    y = y / yn
    z = z / zn

    # Convert to LAB
    def f(t):
        return t ** (1/3) if t > 0.008856 else 7.787 * t + 16/116

    fx = f(x)
    fy = f(y)
    fz = f(z)

    L = 116 * fy - 16
    a = 500 * (fx - fy)
    b = 200 * (fy - fz)

    return L, a, b

def lab_to_xyz(L, a, b):
    """Convert LAB color space to XYZ color space."""
    # D65 illuminant reference values
    xn, yn, zn = 95.047, 100.0, 108.883

    fy = (L + 16) / 116
    fx = a / 500 + fy
    fz = fy - b / 200

    def f_inv(t):
        return t**3 if t > 0.206893 else (t - 16/116) / 7.787

    x = xn * f_inv(fx)
    y = yn * f_inv(fy)
    z = zn * f_inv(fz)

    return x, y, z

def xyz_to_rgb(x, y, z):
    """Convert XYZ color space to RGB color space."""
    x = x / 100
    y = y / 100
    z = z / 100

    # Convert to linear RGB
    r = x * 3.2404542 - y * 1.5371385 - z * 0.4985314
    g = -x * 0.9692660 + y * 1.8760108 + z * 0.0415560
    b = x * 0.0556434 - y * 0.2040259 + z * 1.0572252

    # Convert to sRGB
    def to_srgb(c):
        return 255 * (1.055 * c ** (1/2.4) - 0.055) if c > 0.0031308 else 255 * 12.92 * c

    r = max(0, min(255, round(to_srgb(r))))
    g = max(0, min(255, round(to_srgb(g))))
    b = max(0, min(255, round(to_srgb(b))))

    return r, g, b

def lab_distance(lab1, lab2):
    """Calculate the CIEDE2000 color difference between two LAB colors."""
    L1, a1, b1 = lab1
    L2, a2, b2 = lab2
    
    # Simple Euclidean distance in LAB space
    # For a more accurate but complex calculation, implement CIEDE2000
    return math.sqrt((L2 - L1)**2 + (a2 - a1)**2 + (b2 - b1)**2)

def rgb_to_hex(r, g, b):
    """Convert RGB values to hex color code."""
    return f"#{r:02x}{g:02x}{b:02x}"

def generate_distinct_colors(n, min_distance=None, min_contrast=1.5):
    """
    Generate n maximally distinct colors in CIELAB space.
    
    Args:
        n: Number of colors to generate
        min_distance: Minimum CIELAB distance between colors (auto-adjusted if None)
        min_contrast: Minimum contrast ratio between colors
        
    Returns:
        List of (background_hex, foreground_hex) tuples
    """
    colors = []
    attempts = 0
    max_attempts = 10000

    # Auto-adjust min_distance based on number of colors needed
    if min_distance is None:
        if n <= 5:
            min_distance = 30  # Small sets focus on contrast ratio instead
        elif n <= 10:
            min_distance = 20  # Medium sets focus on foreground contrast
        else:
            min_distance = max(10, 30 - (n - 10))  # Large sets focus on LAB distance

    # Define LAB space boundaries for visually pleasing colors
    L_range = (20, 90)  # Wider range for more variety
    chroma_range = (30, 128)  # Control color saturation

    # Helper function to check if a new color is valid
    def is_valid_color(lab_color, rgb_color):
        # Check RGB gamut
        if any(c < 0 or c > 255 for c in rgb_color):
            return False

        # Check distance and contrast with existing colors
        for existing_color in colors:
            if lab_distance(lab_color, existing_color[0]) < min_distance:
                return False
            
            # For small sets, ensure minimum contrast between colors
            if n <= 5:
                new_hex = rgb_to_hex(*rgb_color)
                existing_hex = rgb_to_hex(*existing_color[1])
                if get_contrast_ratio(new_hex, existing_hex) < min_contrast:
                    return False

        return True

    # Try to generate colors with better distribution
    while len(colors) < n and attempts < max_attempts:
        # Use golden ratio for better hue distribution
        golden_ratio = 0.618033988749895
        hue = (attempts * golden_ratio) % 1.0
        
        # Generate color with controlled randomness
        # Bias towards more extreme lightness values for better contrast
        if random.random() < 0.6:  # Reduced chance of extreme lightness
            L = random.choice([
                L_range[0] + random.random() * 20,  # Dark
                L_range[1] - random.random() * 20   # Light
            ])
        else:
            L = L_range[0] + (L_range[1] - L_range[0]) * random.random()
        
        # Use hue to influence a and b values for better distribution
        angle = hue * 2 * math.pi
        # Vary chroma based on lightness for better distribution
        max_chroma = min(128, chroma_range[1] * (1 - abs(L - 55) / 45))
        chroma = chroma_range[0] + random.random() * (max_chroma - chroma_range[0])
        
        a = chroma * math.cos(angle)
        b = chroma * math.sin(angle)

        # Convert to RGB to check if it's valid
        x, y, z = lab_to_xyz(L, a, b)
        r, g, b = xyz_to_rgb(x, y, z)

        lab_color = (L, a, b)
        rgb_color = (r, g, b)

        if is_valid_color(lab_color, rgb_color):
            # Calculate foreground color (white or black) based on luminance
            bg_hex = rgb_to_hex(r, g, b)
            fg_white = get_contrast_ratio(bg_hex, "#FFFFFF")
            fg_black = get_contrast_ratio(bg_hex, "#000000")
            
            # Choose the foreground color with better contrast
            foreground = "#FFFFFF" if fg_white > fg_black else "#000000"
            
            # Check foreground contrast requirements
            if n <= 10:  # Small and medium sets need good foreground contrast
                min_fg_contrast = 4.5 if n > 5 else 1.5  # Medium sets need 4.5:1
                if max(fg_white, fg_black) < min_fg_contrast:
                    attempts += 1
                    continue
            
            colors.append((lab_color, rgb_color, foreground))
        
        attempts += 1

    if len(colors) < n:
        print(f"Warning: Could only generate {len(colors)} distinct colors out of {n} requested")

    # Convert to hex format
    return [(rgb_to_hex(r, g, b), foreground) for _, (r, g, b), foreground in colors]

def get_contrast_ratio(bg_color, fg_color):
    """
    Calculate contrast ratio between background and foreground colors.
    Returns a value between 1 and 21, where higher is better.
    WCAG recommends minimum 4.5:1 for normal text.
    """
    def get_luminance(r, g, b):
        # Convert to sRGB
        r = r / 255
        g = g / 255
        b = b / 255
        
        # Convert to linear RGB
        r = ((r + 0.055) / 1.055) ** 2.4 if r > 0.03928 else r / 12.92
        g = ((g + 0.055) / 1.055) ** 2.4 if g > 0.03928 else g / 12.92
        b = ((b + 0.055) / 1.055) ** 2.4 if b > 0.03928 else b / 12.92
        
        # Calculate luminance
        return 0.2126 * r + 0.7152 * g + 0.0722 * b

    # Convert hex to RGB
    def hex_to_rgb(hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    bg_rgb = hex_to_rgb(bg_color)
    fg_rgb = hex_to_rgb(fg_color)

    bg_luminance = get_luminance(*bg_rgb)
    fg_luminance = get_luminance(*fg_rgb)

    lighter = max(bg_luminance, fg_luminance)
    darker = min(bg_luminance, fg_luminance)

    return (lighter + 0.05) / (darker + 0.05)

if __name__ == "__main__":
    # Example usage
    import random
    colors = generate_distinct_colors(10)
    for bg, fg in colors:
        contrast = get_contrast_ratio(bg, fg)
        print(f"Background: {bg}, Foreground: {fg}, Contrast ratio: {contrast:.2f}:1") 