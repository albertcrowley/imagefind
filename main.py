# This is a sample Python script.
# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import os
import sys
import time

import imagehash
from PIL import Image

import imagefind
from imagefind import file_util
from imagefind.file_util import find_jpeg_files
from imagefind.db import Database, DATE_FORMAT, FileData
import logging
import logging.config
from argparse import ArgumentParser

DB_FILE = "file_info.db"
logger = logging.getLogger("ATC")

def scan(dir_name: str):

    start_time = time.time()

    db = Database(DB_FILE)

    file_list = find_jpeg_files(dir_name)
    for file_name in file_list:

        image = Image.open(file_name)
        image_hash = imagehash.phash(image,6)
        size = os.path.getsize(file_name)
        last_modified = time.strftime(DATE_FORMAT, time.localtime(os.path.getmtime(file_name)))

        fd =FileData(filename=file_name, size=size, file_last_modified=last_modified, phash6=image_hash.__str__())
        db.insert_file_info(fd)
        logger.info(fd)


    end_time = time.time()
    execution_time = end_time - start_time

    return {'run_time': execution_time, 'files_processed': len(file_list)}



# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    parser = ArgumentParser()
    parser.add_argument("-l", "--log", default='WARN', help="Set log level")
    args = vars(parser.parse_args())

    logger.setLevel(logging.DEBUG)
    stdout = logging.StreamHandler(sys.stdout)
    stdout.setFormatter(logging.Formatter("%(name)s: %(message)s"))
    logger.addHandler(stdout)


    db = Database(DB_FILE)
    db.create_table()

    runtime = scan('/mnt/e/home-server/Photos/2000')
    print("Execution time:", runtime)


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
