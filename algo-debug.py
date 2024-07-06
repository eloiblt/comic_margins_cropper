from wand.image import Image
import os

def is_white(pixel, tolerance=15):
    return (
        pixel.red_int8 >= 255 - tolerance
        and pixel.green_int8 >= 255 - tolerance
        and pixel.blue_int8 >= 255 - tolerance
    )


def hasBorder(img: Image):
    width, height = img.size
    width -= 1
    height -= 1
    return (
        not is_white(img[0, 0])
        and not is_white(img[width, 0])
        and not is_white(img[0, height])
        and not is_white(img[width, height])
        and is_white(img[10, 10])
        and is_white(img[width - 10, 10])
        and is_white(img[10, height - 10])
        and is_white(img[width - 10, height - 10])
    )


def remove_white_margins(img: Image):
    if hasBorder(img):
        img.shave(10, 10)

    img.trim(percent_background=0.97)

    return img

for root, dirs, files in os.walk("thorgal"):
        for file in files:
            if not "wip" in file:
                path = os.path.join(root, file)
                with Image(filename=path) as img:
                    processed_img = remove_white_margins(img)
                    processed_img.save(filename=path.replace('.jpg', '') + '_wip.jpg')
                    print(path)