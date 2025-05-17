import os
from app.utils.ai import check_image_quality
from PIL import Image, ImageDraw
import tempfile

def main():
    """Test image resolution validation"""
    print("Testing image resolution validation with new 500x300 minimum requirement:")
    
    # Test case 1: Very low resolution (400x200)
    test_file1 = 'test_lowres.png'
    img1 = Image.new('RGB', (400, 200), color=(255, 255, 255))
    draw = ImageDraw.Draw(img1)
    draw.rectangle([(40, 20), (360, 180)], fill=(0, 0, 0))
    img1.save(test_file1)
    
    # Test case 2: Below minimum width, acceptable height (450x350)
    test_file2 = 'test_below_min_width.png'
    img2 = Image.new('RGB', (450, 350), color=(255, 255, 255))
    draw = ImageDraw.Draw(img2)
    draw.rectangle([(45, 35), (405, 315)], fill=(0, 0, 0))
    img2.save(test_file2)
    
    # Test case 3: Acceptable width, below minimum height (550x250)
    test_file3 = 'test_below_min_height.png'
    img3 = Image.new('RGB', (550, 250), color=(255, 255, 255))
    draw = ImageDraw.Draw(img3)
    draw.rectangle([(55, 25), (495, 225)], fill=(0, 0, 0))
    img3.save(test_file3)
    
    # Test case 4: Exactly minimum requirement (500x300)
    test_file4 = 'test_min_requirement.png'
    img4 = Image.new('RGB', (500, 300), color=(255, 255, 255))
    draw = ImageDraw.Draw(img4)
    draw.rectangle([(50, 30), (450, 270)], fill=(0, 0, 0))
    img4.save(test_file4)
    
    # Test case 5: High resolution (800x600)
    test_file5 = 'test_highres.png'
    img5 = Image.new('RGB', (800, 600), color=(255, 255, 255))
    draw = ImageDraw.Draw(img5)
    draw.rectangle([(80, 60), (720, 540)], fill=(0, 0, 0))
    img5.save(test_file5)
    
    # Run tests
    test_files = [
        (test_file1, "Very low resolution (400x200)"),
        (test_file2, "Below min width (450x350)"),
        (test_file3, "Below min height (550x250)"),
        (test_file4, "Minimum requirement (500x300)"),
        (test_file5, "High resolution (800x600)")
    ]
    
    for file_path, description in test_files:
        print(f"\n--- Testing {description} ---")
        with Image.open(file_path) as img:
            width, height = img.size
            print(f"Image dimensions: {width}x{height}")
        
        is_valid, error_msg = check_image_quality(file_path)
        print(f"Is valid: {is_valid}")
        if error_msg:
            print(f"Error message: {error_msg}")
        else:
            print("No error message (passed validation)")
        
        # Clean up
        os.remove(file_path)

if __name__ == "__main__":
    main() 