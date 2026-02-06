# PDF Chatbot

A simple chatbot system that answers questions based on PDF documents using local LLM models.

## Features

- **Advanced PDF Processing:**
  - OCR for scanned/image-based PDFs
  - Automatic table extraction and formatting
  - Noise reduction and image enhancement
  - Multi-method extraction (pdfplumber, PyPDF2, Tesseract OCR)
  - Handles complex layouts and mixed content
- Parse multiple PDF files to JSON format
- Create searchable embeddings using sentence-transformers
- Question answering using Ollama (local LLM)
- Simple Streamlit web interface
- Shows source citations for answers
- 100% local - no cloud dependencies

## Prerequisites

1. **Python 3.8+**

2. **System Dependencies** (for OCR and advanced features)
   
   **Ubuntu/Debian:**
   ```bash
   sudo apt-get update
   sudo apt-get install -y tesseract-ocr poppler-utils
   ```
   
   **macOS:**
   ```bash
   brew install tesseract poppler
   ```
   
   **Windows:**
   - Tesseract: https://github.com/UB-Mannheim/tesseract/wiki
   - Poppler: https://blog.alivate.com.au/poppler-windows/
   
   See `PARSER_SETUP.md` for detailed installation instructions.

3. **Ollama** - Install from https://ollama.ai
   ```bash
   # After installing Ollama, pull the model:
   ollama pull mistral
   # Or use llama3.2, phi3, etc.
   ```

## Installation

1. Clone or navigate to the project directory:
   ```bash
   cd pdf_chatbot
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. **Test the parser (optional but recommended):**
   ```bash
   python test_parser.py
   ```
   This verifies all OCR and table extraction dependencies are working.

## Setup

1. **Add your PDF files**
   - Place all your PDF files in the `data/pdfs/` folder
   - You can add up to 20 PDFs (or more, adjust as needed)

2. **Run the setup script**
   ```bash
   python setup.py
   ```
   
   This will:
   - Parse all PDFs to JSON format
   - Create embeddings for all text chunks
   - Index them in ChromaDB

## Usage

1. **Configure the model (optional)**
   - Edit `config.py` to change Ollama settings:
   ```python
   OLLAMA_CONFIG = {
       'base_url': 'http://localhost:11434',
       'model': 'mistral',  # Change to your preferred model
       'temperature': 0.7,
       'max_tokens': 2000
   }
   ```
   - See `CONFIG_GUIDE.md` for detailed configuration options

2. **Start the chatbot**
   ```bash
   streamlit run app.py
   ```

3. **Open your browser**
   - The app will automatically open at `http://localhost:8501`
   - If not, navigate to the URL shown in the terminal

4. **Ask questions**
   - Type your question in the chat input
   - The bot will search relevant content and generate an answer
   - Sources (PDF filename and page number) are shown below each answer

## Project Structure

```
pdf_chatbot/
├── app.py                 # Streamlit UI
├── setup.py              # Setup script
├── requirements.txt      # Dependencies
├── data/
│   ├── pdfs/            # Put your PDF files here
│   ├── json/            # Generated JSON files
│   └── chromadb/        # Vector database
└── src/
    ├── pdf_parser.py    # PDF to JSON converter
    ├── indexer.py       # Embedding and indexing
    └── chatbot.py       # Chatbot logic
```

## How It Works

1. **PDF Parsing**: Extracts text from each page of PDFs and saves to JSON
2. **Embedding**: Creates vector embeddings using `all-MiniLM-L6-v2` model
3. **Indexing**: Stores embeddings in ChromaDB for fast similarity search
4. **Query**: When you ask a question:
   - Your question is converted to an embedding
   - Most similar text chunks are retrieved
   - These chunks are sent to Ollama (llama3.2) as context
   - LLM generates an answer based on the context

## Customization

### Change LLM Model
Edit `config.py`:
```python
OLLAMA_CONFIG = {
    'model': 'mistral',  # Change to phi3, llama3.2, etc.
    ...
}
```

### Adjust Parameters
All settings are in `config.py`:
- `temperature`: Response creativity (0.0-1.0)
- `max_tokens`: Response length
- `n_results`: Number of context chunks
- `chunk_size`: Size of text chunks

See `CONFIG_GUIDE.md` for detailed explanations.

## Troubleshooting

**Ollama not found:**
- Make sure Ollama is installed and running
- Check with: `ollama list`

**No PDFs found:**
- Ensure PDFs are in `data/pdfs/` folder
- Run `setup.py` again after adding PDFs

**Out of memory:**
- Use a smaller model (phi3 or llama3.2)
- Reduce chunk_size in indexer.py
- Reduce n_results in chatbot.py

**Slow responses:**
- Normal for local LLMs on CPU
- Use GPU if available (Ollama auto-detects)

## Notes

- First run downloads the embedding model (~80MB)
- Ollama model must be pulled separately
- All processing happens locally - no API keys needed
- Chat history is session-based (cleared on refresh)