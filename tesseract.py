import os
import sys
import subprocess
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
from pdf2image import convert_from_path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
from tkinterdnd2 import DND_FILES, TkinterDnD
from collections import Counter

# Debug information
print("Python Path:", sys.executable)
print("Library Path:", os.environ.get('DYLD_LIBRARY_PATH'))
print("System Path:", os.environ.get('PATH'))

# Check if poppler is accessible
try:
    result = subprocess.run(['pdfinfo', '-v'], capture_output=True, text=True)
    print("Poppler version:", result.stdout)
except Exception as e:
    print("Poppler not found:", e)

# Check if tesseract is accessible
try:
    result = subprocess.run(['tesseract', '--version'], capture_output=True, text=True)
    print("Tesseract version:", result.stdout)
except Exception as e:
    print("Tesseract not found:", e)

class PDFOCRProcessor:
    def __init__(self):
        # Set environment variables explicitly
        os.environ['PATH'] = '/opt/homebrew/bin:' + os.environ.get('PATH', '')
        os.environ['DYLD_LIBRARY_PATH'] = '/opt/homebrew/lib:' + os.environ.get('DYLD_LIBRARY_PATH', '')
        
        # Initialize paths
        self.poppler_path = '/opt/homebrew/bin'
        pytesseract.pytesseract.tesseract_cmd = '/opt/homebrew/bin/tesseract'
        
        # OCR settings
        self.ocr_config = r'--oem 3 --psm 3'
        self.dpi = 300
        self.preprocessing_enabled = True
        self.multiple_attempts = 5
        
        # Initialize UI
        self.root = TkinterDnD.Tk()
        self.root.title("Enhanced PDF OCR Processor")
        self.root.geometry("500x400")
        self.setup_ui()

    def preprocess_image(self, image):
        """Apply various preprocessing techniques using PIL"""
        print("Starting image preprocessing...")
        
        # Convert to grayscale
        image = image.convert('L')
        
        # Apply binary threshold
        image = image.point(lambda x: 0 if x < 128 else 255, '1')
        
        # Apply median filter to reduce noise
        image = image.filter(ImageFilter.MedianFilter(size=3))
        
        print("Image preprocessing completed")
        return image

    def enhance_image(self, image):
        """Apply PIL enhancements"""
        print("Applying image enhancements...")
        
        # Convert back to RGB for enhancements
        image = image.convert('RGB')
        
        # Increase contrast
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(2.0)
        
        # Increase sharpness
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(1.5)
        
        # Apply slight brightness adjustment
        enhancer = ImageEnhance.Brightness(image)
        image = enhancer.enhance(1.1)
        
        print("Image enhancement completed")
        return image

    def setup_ui(self):
        # Main frame
        self.frame = tk.Frame(self.root, padx=20, pady=20)
        self.frame.pack(expand=True, fill='both')

        # Settings frame
        settings_frame = ttk.LabelFrame(self.frame, text="OCR Settings", padding=10)
        settings_frame.pack(fill='x', pady=(0, 10))

        # DPI setting
        ttk.Label(settings_frame, text="DPI:").grid(row=0, column=0, padx=5)
        self.dpi_var = tk.StringVar(value=str(self.dpi))
        dpi_combo = ttk.Combobox(settings_frame, textvariable=self.dpi_var, 
                                values=['150', '300', '450', '600'], width=10)
        dpi_combo.grid(row=0, column=1, padx=5)

        # Preprocessing toggle
        self.preprocess_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(settings_frame, text="Enable Preprocessing", 
                       variable=self.preprocess_var).grid(row=0, column=2, padx=5)

        # OCR Mode setting
        ttk.Label(settings_frame, text="OCR Mode:").grid(row=1, column=0, padx=5, pady=5)
        self.ocr_mode_var = tk.StringVar(value="Accurate")
        mode_combo = ttk.Combobox(settings_frame, textvariable=self.ocr_mode_var, 
                                 values=['Fast', 'Accurate', 'Very Accurate'], width=15)
        mode_combo.grid(row=1, column=1, columnspan=2, padx=5, pady=5)

        # Instructions label
        self.label = tk.Label(
            self.frame,
            text="Drag and drop a PDF file here\nor click to select",
            width=40,
            height=8,
            relief="solid"
        )
        self.label.pack(expand=True, fill='both', pady=20)

        # Progress frame
        progress_frame = ttk.Frame(self.frame)
        progress_frame.pack(fill='x', pady=(0, 10))
        
        self.progress_label = ttk.Label(progress_frame, text="")
        self.progress_label.pack(side='top')
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='determinate')
        self.progress_bar.pack(fill='x', pady=(5, 0))

        # Setup drag and drop
        self.label.drop_target_register(DND_FILES)
        self.label.dnd_bind('<<Drop>>', self.on_drop)
        self.label.bind("<Button-1>", lambda e: self.select_file())

    def update_progress(self, current, total):
        progress = (current / total) * 100
        self.progress_bar['value'] = progress
        self.root.update_idletasks()

    def process_page(self, image, page_num, total_pages):
        """Process a single page with smarter OCR attempts"""
        print(f"Processing page {page_num} of {total_pages}")
        self.progress_label.config(text=f"Processing page {page_num} of {total_pages}...")
        self.update_progress(page_num - 1, total_pages)

        # Apply preprocessing if enabled
        if self.preprocess_var.get():
            processed_image = self.preprocess_image(image)
            processed_image = self.enhance_image(processed_image)
        else:
            processed_image = image

        # Adjust OCR configuration based on selected mode
        mode = self.ocr_mode_var.get()
        if mode == "Fast":
            attempts = 2
            config = r'--oem 3 --psm 3'
        elif mode == "Accurate":
            attempts = 3
            config = r'--oem 3 --psm 3'
        else:  # Very Accurate
            attempts = 4
            config = r'--oem 3 --psm 3 -c tessedit_char_blacklist=|'

        # Multiple OCR attempts with different preprocessing
        ocr_results = []
        confidence_scores = []
        
        for attempt in range(attempts):
            print(f"OCR attempt {attempt + 1} of {attempts} for page {page_num}")
            try:
                # Apply different preprocessing for each attempt
                if attempt == 1:
                    # Increase contrast more for second attempt
                    enhancer = ImageEnhance.Contrast(processed_image)
                    attempt_image = enhancer.enhance(2.5)
                elif attempt == 2:
                    # Increase sharpness more for third attempt
                    enhancer = ImageEnhance.Sharpness(processed_image)
                    attempt_image = enhancer.enhance(2.0)
                elif attempt == 3:
                    # Adjust brightness for fourth attempt
                    enhancer = ImageEnhance.Brightness(processed_image)
                    attempt_image = enhancer.enhance(1.2)
                else:
                    attempt_image = processed_image

                # Get OCR data including confidence scores
                ocr_data = pytesseract.image_to_data(attempt_image, config=config, output_type=pytesseract.Output.DICT)
                
                # Calculate average confidence for this attempt
                confidences = [float(conf) for conf in ocr_data['conf'] if conf != '-1']
                avg_confidence = sum(confidences) / len(confidences) if confidences else 0
                print(f"Average confidence for attempt {attempt + 1}: {avg_confidence:.2f}%")
                
                text = pytesseract.image_to_string(attempt_image, config=config)
                
                # Only keep results if confidence is good enough
                if avg_confidence > 60:  # Adjust this threshold as needed
                    ocr_results.append(text)
                    confidence_scores.append(avg_confidence)
                
            except Exception as e:
                print(f"OCR attempt {attempt + 1} failed: {str(e)}")
                continue

        # Use confidence scores to weight the voting
        if confidence_scores:
            # Normalize confidence scores
            max_conf = max(confidence_scores)
            weights = [score/max_conf for score in confidence_scores]
            
            # Split texts into words and weight them
            weighted_words = []
            for text, weight in zip(ocr_results, weights):
                words = text.split()
                weighted_words.extend([(word, weight) for word in words])
            
            # Count weighted occurrences of each word
            word_counts = {}
            for word, weight in weighted_words:
                word_counts[word] = word_counts.get(word, 0) + weight
            
            # Reconstruct text using most weighted words
            final_text = ' '.join([word for word, _ in 
                                 sorted(word_counts.items(), 
                                       key=lambda x: word_counts[x[0]], 
                                       reverse=True)])
        else:
            # Fallback to simple voting if confidence scores are unavailable
            final_text = Counter(ocr_results).most_common(1)[0][0] if ocr_results else "Page processing failed"

        print(f"Page {page_num} processing completed")
        return final_text

    def process_pdf(self, file_path):
        try:
            print(f"\nProcessing file: {file_path}")
            print(f"Poppler path: {self.poppler_path}")
            
            self.progress_label.config(text="Converting PDF to images...")
            self.root.update()

            # Convert PDF to images with current DPI setting
            try:
                print("Starting PDF to image conversion...")
                images = convert_from_path(
                    file_path,
                    poppler_path=self.poppler_path,
                    dpi=int(self.dpi_var.get())
                )
                print(f"PDF conversion complete. Found {len(images)} pages")
            except Exception as e:
                print(f"Error during PDF conversion: {str(e)}")
                raise

            print(f"Successfully converted PDF to {len(images)} images")
            full_text = ""
            total_pages = len(images)

            for page_num, image in enumerate(images, 1):
                try:
                    print(f"\nStarting processing of page {page_num} of {total_pages}")
                    text = self.process_page(image, page_num, total_pages)
                    print(f"Successfully processed page {page_num}")
                    
                    # Add page separator and text
                    page_text = f"\n{'=' * 50}\nPage {page_num}\n{'=' * 50}\n\n{text}\n"
                    full_text += page_text
                    
                    # Save progress after each page (in case of crashes)
                    temp_output_file = os.path.splitext(file_path)[0] + f"_OCR_temp.txt"
                    with open(temp_output_file, "w", encoding='utf-8') as f:
                        f.write(full_text)
                    print(f"Saved progress through page {page_num}")
                    
                except Exception as e:
                    print(f"Error processing page {page_num}: {str(e)}")
                    error_text = f"\n{'=' * 50}\nPage {page_num} (Error occurred)\n{'=' * 50}\n\nError: {str(e)}\n"
                    full_text += error_text
                    continue  # Continue with next page even if one fails

            # Save the final text to a file
            output_file = os.path.splitext(file_path)[0] + "_OCR.txt"
            try:
                with open(output_file, "w", encoding='utf-8') as f:
                    f.write(full_text)
                print(f"Successfully saved complete output to: {output_file}")
                
                # Clean up temp file if it exists
                if os.path.exists(temp_output_file):
                    os.remove(temp_output_file)
            except Exception as e:
                print(f"Error saving final output: {str(e)}")
                raise

            self.progress_bar['value'] = 100
            messagebox.showinfo("Success", f"OCR complete!\nOutput saved to:\n{output_file}")
            self.progress_label.config(text="")
            self.progress_bar['value'] = 0

        except Exception as e:
            print(f"Critical error occurred: {str(e)}")
            messagebox.showerror("Error", f"An error occurred:\n{str(e)}")
            self.progress_label.config(text="")
            self.progress_bar['value'] = 0

    def on_drop(self, event):
        file_path = event.data
        if file_path.lower().endswith('.pdf'):
            threading.Thread(target=self.process_pdf, args=(file_path,), daemon=True).start()
        else:
            messagebox.showerror("Error", "Please select a PDF file")

    def select_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("PDF Files", "*.pdf")],
            title="Select a PDF file"
        )
        if file_path:
            threading.Thread(target=self.process_pdf, args=(file_path,), daemon=True).start()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = PDFOCRProcessor()
    app.run()
