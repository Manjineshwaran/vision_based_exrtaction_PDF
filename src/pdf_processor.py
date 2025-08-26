# import os
# from pdf2image import convert_from_path
# from .config import Config

# class PDFProcessor:
#     def __init__(self, poppler_path=Config.POPPLER_PATH):
#         self.poppler_path = poppler_path
    
#     def convert_pdf_to_images(self, pdf_path, output_dir=Config.DEFAULT_OUTPUT_DIR):
#         """
#         Convert PDF pages to images
        
#         Args:
#             pdf_path (str): Path to the PDF file
#             output_dir (str): Directory to save the images
            
#         Returns:
#             list: List of paths to the generated images
#         """
#         os.makedirs(output_dir, exist_ok=True)
        
#         # Convert PDF to images
#         pages = convert_from_path(pdf_path, poppler_path=self.poppler_path)
        
#         # Save images
#         image_paths = []
#         for i, page in enumerate(pages, start=1):
#             out_file = os.path.join(output_dir, f"page_{i}.jpg")
#             page.save(out_file, "JPEG")
import os
import fitz  # PyMuPDF
from pdf2image import convert_from_path
from .config import Config

class PDFProcessor:
    def __init__(self):
        self.poppler_path = Config.get_poppler_path()
    
    def get_page_count(self, pdf_path):
        """
        Get the total number of pages in a PDF file
        
        Args:
            pdf_path (str): Path to the PDF file
            
        Returns:
            int: Total number of pages in the PDF
        """
        try:
            with fitz.open(pdf_path) as doc:
                return len(doc)
        except Exception as e:
            raise Exception(f"Failed to get page count: {e}")
    
    def convert_pdf_page_to_image(self, pdf_path, page_num, output_dir=Config.DEFAULT_OUTPUT_DIR):
        """
        Convert a single PDF page to an image
        
        Args:
            pdf_path (str): Path to the PDF file
            page_num (int): Page number to convert (1-based index)
            output_dir (str): Directory to save the image
            
        Returns:
            str: Path to the generated image
        """
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, f"page_{page_num}.jpg")
        
        try:
            # Convert single page to image
            if self.poppler_path:
                pages = convert_from_path(
                    pdf_path,
                    first_page=page_num,
                    last_page=page_num,
                    poppler_path=self.poppler_path
                )
            else:
                pages = convert_from_path(
                    pdf_path,
                    first_page=page_num,
                    last_page=page_num
                )
            
            if pages:
                pages[0].save(output_file, "JPEG")
                print(f"Saved {output_file}")
                return output_file
            return None
            
        except Exception as e:
            print(f"Error converting page {page_num}: {e}")
            return None
    
    def convert_pdf_to_images(self, pdf_path, output_dir=Config.DEFAULT_OUTPUT_DIR):
        """
        Convert all PDF pages to images
        
        Args:
            pdf_path (str): Path to the PDF file
            output_dir (str): Directory to save the images
            
        Returns:
            list: List of paths to the generated images
        """
        total_pages = self.get_page_count(pdf_path)
        image_paths = []
        
        for page_num in range(1, total_pages + 1):
            img_path = self.convert_pdf_page_to_image(pdf_path, page_num, output_dir)
            if img_path:
                image_paths.append(img_path)
        
        return image_paths