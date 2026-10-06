"""
PDF Text Extractor Tool - Extract text content from PDF files using multiple methods
"""

import PyPDF2
import pdfplumber
from typing import Union, Dict, Any, Optional
import os


def execute(
    pdf_path: str, 
    method: str = "pdfplumber", 
    page_range: Optional[tuple] = None,
    extract_tables: bool = False,
    clean_text: bool = True
) -> Dict[str, Any]:
    """
    Extract text content from PDF files with multiple extraction methods.
    
    Args:
        pdf_path: Path to the PDF file
        method: Extraction method ('pdfplumber', 'pypdf2', 'both')
        page_range: Tuple (start_page, end_page) for partial extraction (0-indexed)
        extract_tables: Whether to extract tables (pdfplumber only)
        clean_text: Whether to clean extracted text (remove extra whitespace)
    
    Returns:
        Dictionary containing extracted text, metadata, and optional tables
    """
    
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    
    result = {
        "file_path": pdf_path,
        "method": method,
        "text": "",
        "pages": [],
        "metadata": {},
        "tables": [] if extract_tables else None
    }
    
    try:
        if method in ["pdfplumber", "both"]:
            result.update(_extract_with_pdfplumber(pdf_path, page_range, extract_tables, clean_text))
        
        if method in ["pypdf2", "both"]:
            pypdf2_result = _extract_with_pypdf2(pdf_path, page_range, clean_text)
            if method == "both":
                result["pypdf2_text"] = pypdf2_result["text"]
                result["pypdf2_pages"] = pypdf2_result["pages"]
            else:
                result.update(pypdf2_result)
                
    except Exception as e:
        result["error"] = str(e)
        result["text"] = ""
    
    return result


def _extract_with_pdfplumber(pdf_path: str, page_range: Optional[tuple], extract_tables: bool, clean_text: bool) -> Dict[str, Any]:
    """Extract text using pdfplumber (better for layout and tables)."""
    result = {"text": "", "pages": [], "metadata": {}, "tables": []}
    
    with pdfplumber.open(pdf_path) as pdf:
        result["metadata"] = {
            "total_pages": len(pdf.pages),
            "method": "pdfplumber"
        }
        
        pages_to_process = pdf.pages
        if page_range:
            start, end = page_range
            pages_to_process = pdf.pages[start:end+1]
        
        for i, page in enumerate(pages_to_process):
            page_text = page.extract_text() or ""
            
            if clean_text:
                page_text = _clean_text(page_text)
            
            result["pages"].append({
                "page_number": i + (page_range[0] if page_range else 0),
                "text": page_text,
                "char_count": len(page_text)
            })
            
            result["text"] += page_text + "\n"
            
            # Extract tables if requested
            if extract_tables:
                tables = page.extract_tables()
                for table in tables:
                    result["tables"].append({
                        "page_number": i + (page_range[0] if page_range else 0),
                        "table_data": table
                    })
    
    return result


def _extract_with_pypdf2(pdf_path: str, page_range: Optional[tuple], clean_text: bool) -> Dict[str, Any]:
    """Extract text using PyPDF2 (faster, simpler)."""
    result = {"text": "", "pages": [], "metadata": {}}
    
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        
        result["metadata"] = {
            "total_pages": len(pdf_reader.pages),
            "method": "pypdf2"
        }
        
        pages_to_process = range(len(pdf_reader.pages))
        if page_range:
            start, end = page_range
            pages_to_process = range(start, min(end + 1, len(pdf_reader.pages)))
        
        for i in pages_to_process:
            page = pdf_reader.pages[i]
            page_text = page.extract_text()
            
            if clean_text:
                page_text = _clean_text(page_text)
            
            result["pages"].append({
                "page_number": i,
                "text": page_text,
                "char_count": len(page_text)
            })
            
            result["text"] += page_text + "\n"
    
    return result


def _clean_text(text: str) -> str:
    """Clean extracted text by removing extra whitespace and formatting."""
    if not text:
        return ""
    
    # Remove excessive whitespace
    import re
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\n\s*\n', '\n\n', text)
    
    return text.strip()
