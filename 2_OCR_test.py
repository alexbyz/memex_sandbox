

import pdf2image    # extracts images from PDF
import pytesseract  # interacts with Tesseract, which extracts text from images
import PyPDF2       # cleans PDFs

image = "./_misc/sample.png"
text = pytesseract.image_to_string(image, lang="eng")

print("="*80)
print(text)
print("="*80)