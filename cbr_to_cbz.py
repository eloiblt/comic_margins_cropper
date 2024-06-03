import os
import zipfile
import rarfile
import time
import glob
import shutil
import argparse

def process(input_path, output_path):
    os.makedirs(temp_dir, exist_ok=True)

    with rarfile.RarFile(input_path, 'r') as rar_ref:
        rar_ref.extractall(temp_dir)

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

    files = glob.glob(path + '/**/*.cbr', recursive=True)

    i = 0
    for file in files:
        output_file = file.replace('.cbr', '.cbz')

        process(file, output_file)

        i += 1
        print(f'{round(i / len(files) * 100, 0)}%')

        clean_temp_folder()

parser = argparse.ArgumentParser(description='CBR to CBZ conversion tool.')
parser.add_argument('path', type=str, help='Folder path to work on')
args = parser.parse_args()

path = args.path
temp_dir = os.path.join(path, "temp")

start_time = time.time()
process_files_in_current_directory()
print(f'{round(time.time() - start_time, 2)}s')