import argparse
import os
import pytesseract
from PIL import Image, ImageOps
from pdf2image import convert_from_path
import glob

def convert_pdf_to_images(pdf_path, output_folder):
    """
    Convert the input pdf into a set of images saved in the output_folder.
    Return the list of image file paths.
    """
    images = convert_from_path(pdf_path)
    image_files = []
    for i, image in enumerate(images):
        image_file = os.path.join(output_folder, f"page_{i}.png")
        image.save(image_file)
        image_files.append(image_file)
    return image_files

def apply_greyscale(image_path):
    """
    Apply greyscale to the image at the input path. Save the greyscale image at the same path.
    """
    image = Image.open(image_path)
    gray_image = ImageOps.grayscale(image)
    gray_image.save(image_path)

def ocr_image(image_path, language):
    """
    Perform OCR on the image at the input path using the specified language.
    Return the resulting text.
    """
    return pytesseract.image_to_string(Image.open(image_path), lang=language)

def main():
    parser = argparse.ArgumentParser(description="Perform OCR on a PDF.")
    parser.add_argument("input_file", help="Path to the input PDF file.")
    parser.add_argument("-l", "--lang", default="eng", help="Language for Tesseract OCR.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Increase output verbosity.")
    parser.add_argument("--list-langs", action="store_true", help="List available Tesseract languages.")

    args = parser.parse_args()

    input_file = args.input_file
    language = args.lang
    verbose = args.verbose

    output_dir = os.path.join(os.path.dirname(input_file), os.path.splitext(os.path.basename(input_file))[0])
    os.makedirs(output_dir, exist_ok=True)

    if verbose:
        print(f"Converting PDF {input_file} to images...")
    image_files = convert_pdf_to_images(input_file, output_dir)

    ocr_texts = []
    for image_file in image_files:
        if verbose:
            print(f"Applying grayscale to image {image_file}...")
        apply_greyscale(image_file)

        if verbose:
            print(f"Running OCR on image {image_file}...")
        ocr_texts.append(ocr_image(image_file, language))

    output_file = f"{output_dir}.txt"
    with open(output_file, "w") as f:
        f.write("\n".join(ocr_texts))

    if verbose:
        print(f"OCR complete. Output saved to {output_file}")

if __name__ == "__main__":
    main()
