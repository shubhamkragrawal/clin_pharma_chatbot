# PDF Chatbot

A local chatbot that answers questions based on your PDF documents using OCR, table extraction, and local LLM.

## Features

- Parse any PDF type (native, scanned, tables, images)
- OCR for scanned documents
- Automatic table extraction
- Local LLM (no API keys needed)
- Source citations with page numbers

## Quick Start

### 1. Install Dependencies

**macOS:**
```bash
brew install tesseract poppler ollama
ollama pull mistral
pip3 install -r requirements.txt
```

**Linux:**
```bash
sudo apt-get install tesseract-ocr poppler-utils
ollama pull mistral
pip3 install -r requirements.txt
```

### 2. Add Your PDFs

```bash
# Place PDF files in data/pdfs/
cp your_files.pdf data/pdfs/
```

### 3. Run Setup

```bash
python3 setup.py
```

### 4. Start Chatbot

```bash
streamlit run app.py
```

Open: http://localhost:8501

## Configuration

Edit `config.py` to customize:
- LLM model and parameters
- OCR quality and language
- Table extraction settings

## Documentation

- `QUICKSTART.md` - Fast setup guide
- `PARSER_SETUP.md` - OCR installation details
- `CONFIG_GUIDE.md` - Configuration options
- `PARSER_FEATURES.md` - Advanced parser features

## Troubleshooting

**Test dependencies:**
```bash
python3 test_parser.py
python3 test_ollama.py
```

**View database:**
```bash
python3 view_database.py
```

**Re-run with new PDFs:**
```bash
python3 setup.py
streamlit run app.py
```

## Tech Stack

- PDF: pdfplumber, Tesseract OCR, Camelot
- Embeddings: sentence-transformers
- Vector DB: ChromaDB
- LLM: Ollama (mistral)
- UI: Streamlit

100% local - no cloud dependencies.