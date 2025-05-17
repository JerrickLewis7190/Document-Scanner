from PIL import Image, ImageEnhance, ExifTags
import os

def preprocess_image(input_path, output_path=None, max_width=2048):
    """
    Preprocess the image for better GPT-4 Vision extraction:
    - Auto-orient using EXIF
    - Resize if too large
    - Mild brightness/contrast enhancement
    - Save as PNG
    Returns the path to the processed image.
    """
    image = Image.open(input_path)

    # 1. Auto-orient
    try:
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation] == 'Orientation':
                break
        exif = dict(image._getexif().items())
        if exif[orientation] == 3:
            image = image.rotate(180, expand=True)
        elif exif[orientation] == 6:
            image = image.rotate(270, expand=True)
        elif exif[orientation] == 8:
            image = image.rotate(90, expand=True)
    except Exception:
        pass  # No EXIF data or orientation info

    # 2. Resize if too large
    if image.width > max_width:
        ratio = max_width / image.width
        new_size = (max_width, int(image.height * ratio))
        image = image.resize(new_size, Image.LANCZOS)

    # 3. Mild brightness/contrast enhancement
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(1.1)  # Slightly increase contrast
    enhancer = ImageEnhance.Brightness(image)
    image = enhancer.enhance(1.05)  # Slightly increase brightness

    # 4. Save as PNG
    if output_path is None:
        base, _ = os.path.splitext(input_path)
        output_path = base + "_preprocessed.png"
    image.save(output_path, format='PNG')
    return output_path 