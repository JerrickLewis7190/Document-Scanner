from app.utils.ai import check_image_quality
from PIL import Image, ImageDraw
import os
import time

# Test each resolution individually
def test_resolution(width, height):
    """Test a specific resolution"""
    print(f"\n--- Testing resolution: {width}x{height} ---")
    
    # Create test image with more distinct visual content
    filename = f"test_{width}x{height}.png"
    img = Image.new('RGB', (width, height), color=(240, 240, 240))
    draw = ImageDraw.Draw(img)
    
    # Add a black rectangle
    draw.rectangle([(width*0.2, height*0.2), (width*0.8, height*0.8)], fill=(30, 30, 30))
    
    # Add some text-like lines to simulate content
    for i in range(5):
        y_pos = height * (0.3 + i * 0.1)
        draw.line([(width*0.3, y_pos), (width*0.7, y_pos)], fill=(200, 200, 200), width=3)
    
    # Save the image
    img.save(filename)
    
    # Check image dimensions
    with Image.open(filename) as check_img:
        print(f"Created image dimensions: {check_img.size[0]}x{check_img.size[1]}")
    
    # Check resolution
    is_valid, error_msg = check_image_quality(filename)
    
    print(f"Is valid: {is_valid}")
    if error_msg:
        print(f"Error message: {error_msg}")
    else:
        print("No error message (image passed validation)")
    
    # Cleanup
    os.remove(filename)
    # Add a small delay to ensure terminal output is flushed
    time.sleep(0.1)

print("Testing image resolution validation with new 500x300 minimum requirement:")

# Test various resolutions
test_resolution(400, 200)  # Below min in both dimensions
test_resolution(450, 350)  # Below min width, acceptable height
test_resolution(550, 250)  # Acceptable width, below min height
test_resolution(500, 300)  # Exactly minimum requirement
test_resolution(800, 600)  # High resolution 