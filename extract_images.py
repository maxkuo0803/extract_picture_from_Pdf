import fitz  # PyMuPDF
from PIL import Image
import io
import os
import shutil

# Configuration
INPUT_DIR = 'input'
OUTPUT_DIR = 'output'
COMPLETED_DIR = 'completed'

def ensure_directories():
    for d in [INPUT_DIR, OUTPUT_DIR, COMPLETED_DIR]:
        if not os.path.exists(d):
            os.makedirs(d)

def pad_to_square(image: Image.Image, color=(255, 255, 255)) -> Image.Image:
    """Pads an image to 1:1 ratio with the specified color."""
    width, height = image.size
    if width == height:
        return image
    
    max_dim = max(width, height)
    new_image = Image.new("RGB", (max_dim, max_dim), color)
    
    # Calculate position to center the image
    left = (max_dim - width) // 2
    top = (max_dim - height) // 2
    
    new_image.paste(image, (left, top))
    return new_image

def process_pdf(pdf_path, output_root=OUTPUT_DIR, move_to_completed=True):
    filename = os.path.basename(pdf_path)
    base_name = os.path.splitext(filename)[0]
    
    # Create specific output folder: {pdf_name}圖片
    pdf_output_folder = os.path.join(output_root, f"{base_name}圖片")
    if not os.path.exists(pdf_output_folder):
        os.makedirs(pdf_output_folder)
    
    try:
        doc = fitz.open(pdf_path)
        print(f"Processing: {filename} with {len(doc)} pages")
        
        image_count = 0
        
        for i, page in enumerate(doc):
            # Get all images on the page
            image_list = page.get_images()
            
            for img_index, img in enumerate(image_list):
                xref = img[0]
                
                # Get the bounding box (rect) of the image on the page
                # get_image_rects returns a list of Rect objects (one for each time the image appears)
                rects = page.get_image_rects(xref)
                
                if not rects:
                    print(f"  Warning: No rect found for image {img_index} on page {i}, skipping.")
                    continue

                # Process each occurrence of the image
                for rect_index, rect in enumerate(rects):
                    try:
                        # Render the area of the image (clip=rect)
                        # Matrix(3, 3) increases resolution by 3x for better quality
                        pix = page.get_pixmap(clip=rect, matrix=fitz.Matrix(3, 3))
                        
                        # Convert to PIL Image
                        mode = "RGBA" if pix.alpha else "RGB"
                        image = Image.frombytes(mode, [pix.width, pix.height], pix.samples)
                        
                        # Pad to 1:1
                        square_image = pad_to_square(image)
                        
                        # Save
                        image_filename = f"image_{i+1}_{img_index+1}_{rect_index+1}.png"
                        save_path = os.path.join(pdf_output_folder, image_filename)
                        square_image.save(save_path, "PNG")
                        image_count += 1
                        
                    except Exception as e:
                        print(f"  Error processing image {img_index} (rect {rect_index}) on page {i}: {e}")

        doc.close()
        print(f"  Extracted {image_count} images.")
        
        if move_to_completed:
            # Move to completed
            destination = os.path.join(COMPLETED_DIR, filename)
            # Handle duplicate filenames in completed
            if os.path.exists(destination):
                base, ext = os.path.splitext(filename)
                counter = 1
                while os.path.exists(os.path.join(COMPLETED_DIR, f"{base}_{counter}{ext}")):
                    counter += 1
                destination = os.path.join(COMPLETED_DIR, f"{base}_{counter}{ext}")
                
            shutil.move(pdf_path, destination)
            print(f"  Moved PDF to {destination}")

    except Exception as e:
        print(f"Error opening or processing {filename}: {e}")

def main():
    ensure_directories()
    
    files = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith('.pdf')]
    
    if not files:
        print("No PDF files found in 'input' folder.")
        return

    print(f"Found {len(files)} PDF files.")
    for f in files:
        process_pdf(os.path.join(INPUT_DIR, f))
    
    print("\nAll tasks finished.")

if __name__ == "__main__":
    main()
