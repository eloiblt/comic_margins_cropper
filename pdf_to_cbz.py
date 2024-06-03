import os
import zipfile
import fitz
import time
import glob
import shutil
import argparse
from PIL import Image

def process(input_path, output_path):
    pdf_document = fitz.open(input_path)

    os.makedirs(temp_dir, exist_ok=True)

    image_paths = []
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        pix = page.get_pixmap(dpi=300)

        img_path = os.path.join(temp_dir, f'page_{page_num + 1}.jpg')
        pix.save(img_path)  # Sauvegarder l'image
        image_paths.append(img_path)

    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for img_path in image_paths:
            zipf.write(img_path, os.path.basename(img_path))

    for img_path in image_paths:
        os.remove(img_path)
    os.rmdir(temp_dir)

def clean_temp_folder():
    shutil.rmtree(temp_dir, ignore_errors=True)

def process_files_in_current_directory():
    clean_temp_folder()

    files = glob.glob(path + '/**/*.pdf', recursive=True)

    i = 0
    for file in files:
        output_file = file.replace('.pdf', '.cbz')

        process(file, output_file)

        i += 1
        print(f'{round(i / len(files) * 100, 0)}%')

        clean_temp_folder()

parser = argparse.ArgumentParser(description='PDF to CBZ conversion tool.')
parser.add_argument('path', type=str, help='Folder path to work on')
args = parser.parse_args()

path = args.path
temp_dir = os.path.join(path, "temp")

start_time = time.time()
process_files_in_current_directory()
print(f'{round(time.time() - start_time, 2)}s')