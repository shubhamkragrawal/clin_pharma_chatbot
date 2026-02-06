import os
import json
import re
from pathlib import Path
from typing import Dict, List, Optional

# Multi-library approach for robust parsing
import pdfplumber
from PyPDF2 import PdfReader
from pdf2image import convert_from_path
import pytesseract
from PIL import Image
import cv2
import numpy as np

# Table extraction
try:
    import camelot
    CAMELOT_AVAILABLE = True
except ImportError:
    CAMELOT_AVAILABLE = False

try:
    import tabula
    TABULA_AVAILABLE = True
except ImportError:
    TABULA_AVAILABLE = False


class AdvancedPDFParser:
    def __init__(self, pdf_folder="data/pdfs", json_folder="data/json"):
        self.pdf_folder = pdf_folder
        self.json_folder = json_folder
        os.makedirs(json_folder, exist_ok=True)
        
        # Configuration
        self.use_ocr = True
        self.extract_tables = True
        self.denoise_images = True
        self.min_text_length = 10  # Minimum characters to consider valid text
    
    def preprocess_image(self, image):
        """Clean and enhance image for better OCR"""
        if not self.denoise_images:
            return image
        
        # Convert PIL to numpy array
        img_array = np.array(image)
        
        # Convert to grayscale
        if len(img_array.shape) == 3:
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        else:
            gray = img_array
        
        # Apply denoising
        denoised = cv2.fastNlMeansDenoising(gray, h=10)
        
        # Increase contrast
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(denoised)
        
        # Thresholding to handle background noise
        _, binary = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Convert back to PIL
        return Image.fromarray(binary)
    
    def extract_text_with_ocr(self, pdf_path, page_num):
        """Extract text from scanned PDF using OCR"""
        try:
            # Convert PDF page to image
            images = convert_from_path(
                pdf_path, 
                first_page=page_num, 
                last_page=page_num,
                dpi=300  # Higher DPI for better OCR
            )
            
            if not images:
                return ""
            
            # Preprocess image
            image = self.preprocess_image(images[0])
            
            # Perform OCR
            text = pytesseract.image_to_string(image, lang='eng')
            
            return text.strip()
            
        except Exception as e:
            print(f"    OCR error on page {page_num}: {str(e)}")
            return ""
    
    def extract_tables_from_page(self, pdf_path, page_num):
        """Extract tables from PDF page"""
        tables_text = []
        
        # Try Camelot first (better for complex tables)
        if CAMELOT_AVAILABLE and self.extract_tables:
            try:
                tables = camelot.read_pdf(
                    str(pdf_path), 
                    pages=str(page_num),
                    flavor='lattice',  # For tables with lines
                    strip_text='\n'
                )
                
                for table in tables:
                    df = table.df
                    # Convert table to readable text
                    table_text = f"\n[TABLE]\n{df.to_string(index=False)}\n[/TABLE]\n"
                    tables_text.append(table_text)
                
                # If lattice fails, try stream (for tables without lines)
                if not tables:
                    tables = camelot.read_pdf(
                        str(pdf_path), 
                        pages=str(page_num),
                        flavor='stream'
                    )
                    for table in tables:
                        df = table.df
                        table_text = f"\n[TABLE]\n{df.to_string(index=False)}\n[/TABLE]\n"
                        tables_text.append(table_text)
                        
            except Exception as e:
                pass  # Silently fail, will try other methods
        
        # Fallback to tabula
        if not tables_text and TABULA_AVAILABLE and self.extract_tables:
            try:
                tables = tabula.read_pdf(
                    str(pdf_path),
                    pages=page_num,
                    multiple_tables=True,
                    silent=True
                )
                
                for df in tables:
                    if not df.empty:
                        table_text = f"\n[TABLE]\n{df.to_string(index=False)}\n[/TABLE]\n"
                        tables_text.append(table_text)
                        
            except Exception as e:
                pass  # Silently fail
        
        return "\n".join(tables_text)
    
    def clean_text(self, text):
        """Clean extracted text from noise and artifacts"""
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove common OCR artifacts
        text = re.sub(r'[|]{2,}', '', text)  # Multiple pipes
        text = re.sub(r'_{3,}', '', text)    # Multiple underscores
        text = re.sub(r'-{3,}', '', text)    # Multiple hyphens
        
        # Fix common OCR mistakes
        text = text.replace('|', 'I')  # Pipe to I
        text = text.replace('0', 'O')  # Zero to O in words (careful!)
        
        # Remove standalone special characters
        text = re.sub(r'\s+[^a-zA-Z0-9\s]+\s+', ' ', text)
        
        # Remove page numbers that might be isolated
        text = re.sub(r'\bPage\s+\d+\b', '', text, flags=re.IGNORECASE)
        
        return text.strip()
    
    def extract_text_from_pdf(self, pdf_path):
        """Extract text from PDF using multiple methods"""
        pages_data = []
        
        # Method 1: Try pdfplumber (best for most PDFs)
        print(f"    Trying pdfplumber...")
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    # Extract text
                    text = page.extract_text() or ""
                    
                    # Extract tables
                    tables_text = ""
                    if self.extract_tables:
                        try:
                            tables = page.extract_tables()
                            if tables:
                                for table in tables:
                                    # Convert table to text
                                    table_str = "\n[TABLE]\n"
                                    for row in table:
                                        table_str += " | ".join([str(cell) if cell else "" for cell in row]) + "\n"
                                    table_str += "[/TABLE]\n"
                                    tables_text += table_str
                        except:
                            pass
                    
                    combined_text = text + "\n" + tables_text
                    combined_text = self.clean_text(combined_text)
                    
                    # If text is too short, mark for OCR
                    if len(combined_text) < self.min_text_length:
                        combined_text = ""
                    
                    pages_data.append({
                        "page_number": page_num,
                        "text": combined_text,
                        "extraction_method": "pdfplumber",
                        "needs_ocr": len(combined_text) < self.min_text_length
                    })
        except Exception as e:
            print(f"    pdfplumber failed: {str(e)}")
            pages_data = []
        
        # Method 2: Fallback to PyPDF2 if pdfplumber failed
        if not pages_data:
            print(f"    Trying PyPDF2...")
            try:
                reader = PdfReader(pdf_path)
                for page_num, page in enumerate(reader.pages, 1):
                    text = page.extract_text() or ""
                    text = self.clean_text(text)
                    
                    pages_data.append({
                        "page_number": page_num,
                        "text": text,
                        "extraction_method": "PyPDF2",
                        "needs_ocr": len(text) < self.min_text_length
                    })
            except Exception as e:
                print(f"    PyPDF2 failed: {str(e)}")
        
        # Method 3: OCR for pages with insufficient text
        if self.use_ocr:
            for page_data in pages_data:
                if page_data["needs_ocr"]:
                    print(f"    Running OCR on page {page_data['page_number']}...")
                    ocr_text = self.extract_text_with_ocr(pdf_path, page_data['page_number'])
                    ocr_text = self.clean_text(ocr_text)
                    
                    if len(ocr_text) > len(page_data['text']):
                        page_data['text'] = ocr_text
                        page_data['extraction_method'] = "OCR"
                        page_data['needs_ocr'] = False
        
        # Method 4: Advanced table extraction with Camelot/Tabula
        if self.extract_tables and (CAMELOT_AVAILABLE or TABULA_AVAILABLE):
            print(f"    Extracting tables...")
            for page_data in pages_data:
                page_num = page_data['page_number']
                tables_text = self.extract_tables_from_page(pdf_path, page_num)
                
                if tables_text:
                    # Append tables to existing text
                    page_data['text'] = page_data['text'] + "\n" + tables_text
        
        return pages_data
    
    def parse_all_pdfs(self):
        """Parse all PDFs in the folder and save as JSON"""
        pdf_files = list(Path(self.pdf_folder).glob("*.pdf"))
        
        if not pdf_files:
            print(f"No PDF files found in {self.pdf_folder}")
            return
        
        print(f"Found {len(pdf_files)} PDF files")
        print(f"OCR enabled: {self.use_ocr}")
        print(f"Table extraction enabled: {self.extract_tables}")
        print(f"Camelot available: {CAMELOT_AVAILABLE}")
        print(f"Tabula available: {TABULA_AVAILABLE}")
        print()
        
        for pdf_file in pdf_files:
            print(f"Processing: {pdf_file.name}")
            
            try:
                pages_data = self.extract_text_from_pdf(pdf_file)
                
                # Create JSON structure
                pdf_json = {
                    "filename": pdf_file.name,
                    "total_pages": len(pages_data),
                    "pages": []
                }
                
                # Clean up pages data for JSON
                for page in pages_data:
                    pdf_json["pages"].append({
                        "page_number": page["page_number"],
                        "text": page["text"],
                        "extraction_method": page["extraction_method"]
                    })
                
                # Calculate stats
                total_chars = sum(len(p['text']) for p in pdf_json['pages'])
                ocr_pages = sum(1 for p in pages_data if p['extraction_method'] == 'OCR')
                
                # Save to JSON file
                json_filename = pdf_file.stem + ".json"
                json_path = os.path.join(self.json_folder, json_filename)
                
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(pdf_json, f, indent=2, ensure_ascii=False)
                
                print(f"  ✓ Saved to {json_filename}")
                print(f"    Pages: {len(pages_data)}, Characters: {total_chars}, OCR pages: {ocr_pages}")
                
            except Exception as e:
                print(f"  ✗ Error processing {pdf_file.name}: {str(e)}")
        
        print("\nPDF parsing complete!")


# Keep backward compatibility
class PDFParser(AdvancedPDFParser):
    """Alias for backward compatibility"""
    pass


if __name__ == "__main__":
    parser = AdvancedPDFParser()
    parser.parse_all_pdfs()