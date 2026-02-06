# Configuration for PDF Chatbot

OLLAMA_CONFIG = {
    'base_url': 'http://localhost:11434',
    'model': 'mistral',
    'timeout': 120,
    'temperature': 0.7,
    'max_tokens': 2000
}

# Embedding configuration
EMBEDDING_CONFIG = {
    'model': 'all-MiniLM-L6-v2',
    'chunk_size': 500,
    'chunk_overlap': 50,
    'n_results': 5  # Number of chunks to retrieve
}

# PDF Parser configuration
PARSER_CONFIG = {
    'use_ocr': True,              # Enable OCR for scanned PDFs
    'extract_tables': True,        # Extract tables from PDFs
    'denoise_images': True,        # Clean images before OCR
    'min_text_length': 10,         # Min characters to consider valid
    'ocr_dpi': 300,               # DPI for OCR (higher = better quality, slower)
    'ocr_language': 'eng'         # Tesseract language (eng, fra, deu, etc.)
}

# Paths
PATHS = {
    'pdf_folder': 'data/pdfs',
    'json_folder': 'data/json',
    'db_path': 'data/chromadb'
}