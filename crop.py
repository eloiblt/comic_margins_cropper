import os
import zipfile
import rarfile
from PIL import Image, ImageOps
from pdf2image import convert_from_path
import time

def is_white(r,g,b, tolerance=10):
    return r >= 255 - tolerance and g >= 255 - tolerance and b >= 255 - tolerance

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

    cropped_image = image.crop((margin_left, margin_top, margin_right, margin_bottom))

    return cropped_image

def process_cbr_cbz(input_path, output_path):
    os.makedirs(temp_dir, exist_ok=True)

    if input_path.lower().endswith('.cbz'):
        with zipfile.ZipFile(input_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
    elif input_path.lower().endswith('.cbr'):
        with rarfile.RarFile(input_path, 'r') as rar_ref:
            rar_ref.extractall(temp_dir)

    for root, dirs, files in os.walk(temp_dir):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                image_path = os.path.join(root, file)
                with Image.open(image_path).convert('RGB') as img:
                    processed_img = remove_white_margins(img)
                    processed_img.save(image_path)

    write_cbz(output_path)

def process_pdf(input_path, output_path):
    os.makedirs(temp_dir, exist_ok=True)

    images = convert_from_path(input_path, poppler_path = 'bin')
    print("convert_from_path --- %s seconds ---" % (time.time() - start_time))

    image_paths = []
    for i, image in enumerate(images):
        image_path = os.path.join(temp_dir, f'page_{i + 1}.png')
        processed_img = remove_white_margins(image)
        processed_img.save(image_path)
        image_paths.append(image_path)

    print("write --- %s seconds ---" % (time.time() - start_time))

    write_cbz(output_path)
    print("write_cbz --- %s seconds ---" % (time.time() - start_time))

def write_cbz(output_path):
    with zipfile.ZipFile(output_path, 'w') as zip_ref:
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, temp_dir)
                zip_ref.write(file_path, arcname=arcname)

def process_files_in_current_directory():
    for file in os.listdir('.'):
        if file.lower().endswith('_cropped.cbz'):
            continue

        if file.lower().endswith('.pdf'):
            output_file = file.replace('.pdf', '_cropped.cbz')
            process_pdf(file, output_file)
        elif file.lower().endswith('.cbr') or file.lower().endswith('.cbz'):
            output_file = file.replace('.cbz', '_cropped.cbz')
            output_file = output_file.replace('.pdf', '_cropped.cbz')
            output_file = output_file.replace('.cbr', '_cropped.cbz')
            process_cbr_cbz(file, output_file)

    # clean temp dir
    for root, dirs, files in os.walk(temp_dir, topdown=False):
        for file in files:
            os.remove(os.path.join(root, file))
        for dir in dirs:
            os.rmdir(os.path.join(root, dir))
    os.rmdir(temp_dir)

temp_dir = './temp'
# The number of checks to get the margin on one side
# To prevent to fall between bubbles
calcul_precision = 100

start_time = time.time()
process_files_in_current_directory()
print("--- %s seconds ---" % (time.time() - start_time))