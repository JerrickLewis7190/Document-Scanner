import pikepdf
from PIL import Image
import io
import os
import logging
import tempfile

logger = logging.getLogger(__name__)

def convert_pdf_to_image(pdf_path):
    """
    Convert the first page of a PDF to a PIL Image using pikepdf.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        PIL Image object or None if conversion failed
    """
    try:
        logger.debug(f"Converting PDF to image: {pdf_path}")
        
        # Check if file exists
        if not os.path.exists(pdf_path):
            logger.error(f"PDF file not found: {pdf_path}")
            return None
            
        # Open the PDF
        with pikepdf.Pdf.open(pdf_path) as pdf:
            # Check if PDF has pages
            if len(pdf.pages) == 0:
                logger.warning(f"PDF has no pages: {pdf_path}")
                return None
                
            # Get the first page
            page = pdf.pages[0]
            
            # Check if page has resources and XObjects
            if hasattr(page, "Resources") and hasattr(page.Resources, "XObject"):
                xobj = page.Resources.XObject
                
                # Try to extract embedded images
                for img_name in xobj:
                    img_obj = xobj[img_name]
                    if hasattr(img_obj, "read_raw_bytes"):
                        try:
                            img_data = img_obj.read_raw_bytes()
                            return Image.open(io.BytesIO(img_data))
                        except Exception as e:
                            logger.warning(f"Failed to extract image from XObject: {e}")
                
            # If no embedded images found, use PyMuPDF as fallback
            # since we already have it installed
            logger.debug("No embedded images found, using PyMuPDF as fallback")
            import fitz
            doc = fitz.open(pdf_path)
            page = doc.load_page(0)
            pix = page.get_pixmap()
            
            # Create a temporary file to save the image
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                pix.save(tmp.name)
                img = Image.open(tmp.name)
                img_copy = img.copy()  # Copy before closing file
                
            # Return the image
            return img_copy
            
    except Exception as e:
        logger.error(f"Error converting PDF to image: {e}")
        return None

def convert_pdf_bytes_to_image(pdf_bytes):
    """
    Convert PDF bytes to a PIL Image.
    
    Args:
        pdf_bytes: PDF file as bytes
        
    Returns:
        Tuple of (image_bytes, error_message)
    """
    try:
        # Create a temporary file to save the PDF
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_pdf:
            tmp_pdf.write(pdf_bytes)
            tmp_pdf_path = tmp_pdf.name
        
        # Convert the PDF to an image
        img = convert_pdf_to_image(tmp_pdf_path)
        
        # Clean up the temporary PDF file
        try:
            os.unlink(tmp_pdf_path)
        except Exception as e:
            logger.warning(f"Failed to delete temporary PDF file: {e}")
        
        if img:
            # Convert the image to bytes
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='PNG')
            return img_byte_arr.getvalue(), None
        else:
            return None, "Failed to convert PDF to image"
            
    except Exception as e:
        error_msg = f"Error converting PDF bytes to image: {e}"
        logger.error(error_msg)
        return None, error_msg

def save_image_from_pdf(pdf_path, output_path):
    """
    Convert the first page of a PDF to an image and save it to disk.
    
    Args:
        pdf_path: Path to the PDF file
        output_path: Path to save the image
        
    Returns:
        True if successful, False otherwise
    """
    img = convert_pdf_to_image(pdf_path)
    if img:
        img.save(output_path)
        return True
    return False 