from PIL import Image, ImageOps
import numpy as np

def is_white(r,g,b, tolerance=15):
    return r >= 255 - tolerance and g >= 255 - tolerance and b >= 255 - tolerance

def remove_white_margins(image):
    # The number of checks to get the margin on one side
    # To prevent to fall between bubbles
    calcul_precision = 100

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

    if margin_right < margin_left or margin_bottom < margin_top:
        return image

    cropped_image = image.crop((margin_left, margin_top, margin_right, margin_bottom))

    return cropped_image

with Image.open('003.jpg').convert('RGB') as img:
    processed_img = remove_white_margins(img)
    processed_img.save('003_cropped.jpg')