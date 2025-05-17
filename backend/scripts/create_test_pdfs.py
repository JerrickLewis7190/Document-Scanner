from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import os

def convert_image_to_pdf(image_path, pdf_path):
    """Convert an image to PDF while maintaining aspect ratio"""
    # Open the image
    img = Image.open(image_path)
    
    # Get image size
    width, height = img.size
    
    # Calculate aspect ratio
    aspect = height / float(width)
    
    # Set PDF width to letter size width
    pdf_width = letter[0]
    # Calculate height maintaining aspect ratio
    pdf_height = pdf_width * aspect
    
    # Create the PDF
    c = canvas.Canvas(pdf_path, pagesize=(pdf_width, pdf_height))
    # Draw the image
    c.drawImage(image_path, 0, 0, width=pdf_width, height=pdf_height)
    c.save()

def main():
    # Get the project root directory
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    images_dir = os.path.join(root_dir, 'Images')
    pdfs_dir = os.path.join(root_dir, 'PDFs')
    
    # Create PDFs directory if it doesn't exist
    os.makedirs(pdfs_dir, exist_ok=True)
    
    # Convert each image to PDF
    for image_file in os.listdir(images_dir):
        if image_file.endswith(('.png', '.jpg', '.jpeg')):
            image_path = os.path.join(images_dir, image_file)
            pdf_name = os.path.splitext(image_file)[0] + '.pdf'
            pdf_path = os.path.join(pdfs_dir, pdf_name)
            
            print(f"Converting {image_file} to PDF...")
            convert_image_to_pdf(image_path, pdf_path)
            print(f"Created {pdf_name}")

if __name__ == '__main__':
    main() 