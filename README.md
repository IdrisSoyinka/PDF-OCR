# PDF-OCR
High fidelity optical character recognition
Enhanced PDF OCR Processor
A robust PDF OCR (Optical Character Recognition) processing application with a user-friendly GUI interface. This tool converts PDF documents to searchable text with advanced preprocessing and multiple OCR attempts for improved accuracy.
Features

🖼️ PDF to image conversion with customizable DPI settings
🔍 Multiple OCR processing attempts with confidence scoring
🎨 Advanced image preprocessing and enhancement
⚙️ Configurable OCR modes (Fast, Accurate, Very Accurate)
📊 Progress tracking with visual feedback
🎯 Drag-and-drop interface
💾 Automatic progress saving and error recovery
🔧 Customizable processing settings

Requirements

Python 3.6 or higher
Poppler (PDF rendering engine)
Tesseract OCR engine
Required Python packages:

pdf2image
pytesseract
Pillow (PIL)
tkinterdnd2
tkinter (usually comes with Python)



Installation

Install Python dependencies:

bashCopypip install pdf2image pytesseract Pillow tkinterdnd2

Install Tesseract OCR:


macOS (using Homebrew):

bashCopybrew install tesseract

Linux:

bashCopysudo apt-get install tesseract-ocr

Windows:

Download and install from Tesseract GitHub releases




Install Poppler:


macOS:

bashCopybrew install poppler

Linux:

bashCopysudo apt-get install poppler-utils

Windows:

Download from Poppler releases



Usage

Run the application:

bashCopypython pdf_ocr_processor.py

Use the application in one of two ways:

Drag and drop a PDF file onto the application window
Click the application window to select a PDF file


Configure OCR settings:

DPI: Choose from 150, 300, 450, or 600
Processing Mode: Select Fast, Accurate, or Very Accurate
Enable/disable preprocessing as needed


Monitor progress through the progress bar and status messages
Find the output text file in the same directory as your PDF, with "_OCR" appended to the filename

Advanced Features
OCR Modes

Fast: Quick processing with 2 OCR attempts
Accurate: Balanced processing with 3 OCR attempts and enhanced preprocessing
Very Accurate: Thorough processing with 4 OCR attempts and maximum enhancement

Image Preprocessing
The application includes several preprocessing steps:

Grayscale conversion
Binary thresholding
Noise reduction
Contrast enhancement
Sharpness adjustment
Brightness optimization

Error Handling

Automatic progress saving after each page
Temporary file creation for crash recovery
Detailed error logging
Continues processing remaining pages if one page fails

Troubleshooting
If you encounter issues:

Check the console output for detailed error messages
Verify Tesseract and Poppler are properly installed
Ensure proper permissions for file access
Check system PATH variables include Tesseract and Poppler

Common issues:

"Tesseract not found": Check Tesseract installation and PATH
"Poppler not found": Verify Poppler installation and PATH
"PDF conversion failed": Check PDF file integrity and Poppler installation

Contributing:
Idris Soyinka
Contributions are welcome! Please feel free to submit pull requests, create issues, or suggest improvements.
License
NONE NEEDED
Acknowledgments
This project uses several open-source tools:

Tesseract OCR engine
Poppler PDF rendering engine
Python and its excellent community packages

