# This is a sample Python script.
# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import os
import time

import imagehash
from PIL import Image

import imagefind
from imagefind import file_util
from imagefind.file_util import find_jpeg_files
from imagefind.db import Database, DATE_FORMAT, FileData

DB_FILE = "file_info.db"


def scan(dir_name: str):
    start_time = time.time()

    db = Database(DB_FILE)

    count = 0;

    file_list = find_jpeg_files(dir_name)
    for file_name in file_list:
        count += 1
        if count < 10:

            image = Image.open(file_name)
            image_hash = imagehash.phash(image,6)

            size = os.path.getsize(file_name)
            last_modified = time.strftime(DATE_FORMAT, time.localtime(os.path.getmtime(file_name)))
            print (file_name, image_hash)


            fd =FileData(filename=file_name, size=size, file_last_modified=last_modified, phash6=image_hash.__str__())
            print (fd)

            db.insert_file_info(fd)


    end_time = time.time()
    execution_time = end_time - start_time

    return {'run_time': execution_time, 'files_processed': len(file_list)}



# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    db = Database(DB_FILE)
    db.create_table()


    runtime = scan('/mnt/e/home-server/Photos/2000')
    print("Execution time:", runtime)


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
