import os
import zipfile
import rarfile
from PIL import Image, ImageOps
from pdf2image import convert_from_path
import time
import glob
import shutil
import argparse

def is_white(r,g,b):
    return r >= 255 - white_tolerance and g >= 255 - white_tolerance and b >= 255 - white_tolerance

def remove_white_margins(image):
    width, height = image.size
    step_height = height / calcul_precision
    step_width = width / calcul_precision

    first_white_col = 0
    while not is_white(*image.getpixel((first_white_col, 1))):
        # if the image has no white margins (covers), stop
        if first_white_col > width / 2:
            return image
        first_white_col += 1

    last_white_col = width - 1
    while not is_white(*image.getpixel((last_white_col, 1))):
        # if the image has no white margins (covers), stop
        if last_white_col < width / 2:
            return image
        last_white_col -= 1

    first_white_row = 0
    while not is_white(*image.getpixel((first_white_col, first_white_row))):
        first_white_row += 1

    last_white_row = height - 1
    while not is_white(*image.getpixel((first_white_col, last_white_row))):
        last_white_row -= 1

    margin_left = last_white_col
    margin_right = first_white_col
    margin_top = last_white_row
    margin_bottom = first_white_row

    for i in range(1, calcul_precision):
        y = step_height * i

        # margin left
        x = first_white_col
        while is_white(*image.getpixel((x, y))):
            if (x == margin_left):
                break
            x += 1
        if x < margin_left:
            margin_left = x

        # margin right
        x = last_white_col
        while is_white(*image.getpixel((x, y))):
            if (x == margin_right):
                break
            x -= 1
        if x > margin_right:
            margin_right = x

        x = step_width * i

        # margin top
        y = first_white_row
        while is_white(*image.getpixel((x, y))):
            if (y == margin_top):
                break
            y += 1
        if y < margin_top:
            margin_top = y

        # margin bottom
        y = last_white_row
        while is_white(*image.getpixel((x, y))):
            if (y == margin_bottom):
                break
            y -= 1
        if y > margin_bottom:
            margin_bottom = y

    # white page
    if margin_right < margin_left or margin_bottom < margin_top:
        return image

    margin_left -= 5
    margin_right += 5
    margin_top -= 5
    margin_bottom += 5

    cropped_image = image.crop((margin_left, margin_top, margin_right, margin_bottom))

    return cropped_image

def process(input_path, output_path):
    os.makedirs(temp_dir, exist_ok=True)

    with zipfile.ZipFile(input_path, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)

    for root, dirs, files in os.walk(temp_dir):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                image_path = os.path.join(root, file)
                with Image.open(image_path).convert('RGB') as img:
                    processed_img = remove_white_margins(img)
                    processed_img.save(image_path)

    with zipfile.ZipFile(output_path, 'w') as zip_ref:
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, temp_dir)
                zip_ref.write(file_path, arcname=arcname)

def clean_temp_folder():
    shutil.rmtree(temp_dir, ignore_errors=True)

def process_files_in_current_directory():
    clean_temp_folder()

    files = glob.glob(path + '/**/*.cbz', recursive=True)

    i = 0
    for file in files:
        output_file = file.replace('.cbz', '_cropped.cbz')

        process(file, output_file)

        i += 1
        print(f'{round(i / len(files) * 100, 0)}%')

        clean_temp_folder()

parser = argparse.ArgumentParser(description='Crop CBZ white margin tool.')
parser.add_argument('path', type=str, help='Folder path to work on')
args = parser.parse_args()

path = args.path
temp_dir = os.path.join(path, "temp")
# The number of checks to get the margin on one side
# To prevent to fall between bubbles
calcul_precision = 100
white_tolerance = 30

start_time = time.time()
process_files_in_current_directory()
print(f'{round(time.time() - start_time, 2)}s')