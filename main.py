# This is a sample Python script.
# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import os
import sys
import time

import imagehash
from PIL import Image, UnidentifiedImageError

import progressbar

from tqdm import tqdm
import imagefind
from imagefind import file_util
from imagefind.file_util import find_jpeg_files
from imagefind.db import Database, DATE_FORMAT, FileData
import logging
import logging.config
from argparse import ArgumentParser

DB_FILE = "file_info.db"
logger = logging.getLogger("ATC")
args = None


def find_file_match(db: Database, target: str):
    start_time = time.time()
    image = Image.open(target)
    image_hash = imagehash.phash(image, 6)
    print("looking image {} with hash {}".format(target, image_hash.__str__()))
    found = db.find_by_hash(image_hash.__str__())
    end_time = time.time()
    execution_time = end_time - start_time

    return {'run_time': execution_time, 'matches': found}


def scan(dir_name: str, db: Database):
    start_time = time.time()
    file_list = find_jpeg_files(dir_name)
    count_updated = 0
    for file_name in tqdm(file_list):

        if db.find_by_file_name(file_name) == None:
            try:
                image = Image.open(file_name)
                image_hash = imagehash.phash(image, 6)
                size = os.path.getsize(file_name)
                last_modified = time.strftime(DATE_FORMAT, time.localtime(os.path.getmtime(file_name)))

                fd = FileData(filename=file_name, size=size, file_last_modified=last_modified,
                              phash6=image_hash.__str__())
                db.insert_file_info(fd)
                logger.info(fd)
                count_updated += 1
            except UnidentifiedImageError:
                logger.error("Unidentified image error for {}".format(file_name))
            except:
                logger.error("Unknown error for {}".format(file_name))

    end_time = time.time()
    execution_time = end_time - start_time

    return {'run_time': execution_time, 'files_processed': len(file_list), 'files_updated': count_updated}


def parse_arguments():
    parser = ArgumentParser()
    parser.add_argument("-l", "--log", default='WARN', help="Set log level, choose one of DEBUG, INFO, WARN, ERROR")
    parser.add_argument("-d", "--dir", default='.', help="Directory to use as the base of the scan")
    parser.add_argument("-f", "--find", default=None, help="File to find")
    args = vars(parser.parse_args())
    return args


def setup_logging():
    level = getattr(logging, args['log'].upper())
    logger.setLevel(level)
    stdout = logging.StreamHandler(sys.stdout)
    stdout.setFormatter(logging.Formatter("%(name)s: %(message)s"))
    logger.addHandler(stdout)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    args = parse_arguments()
    setup_logging()

    db = Database(DB_FILE)
    db.create_table()

    if args['dir']:
        logger.info("Scanning " + args['dir'])
        db = Database(DB_FILE)
        runtime = scan(args['dir'], db)
        print("Execution time:", runtime)

    if args['find'] is not None:
        logger.info("Looking for  " + args['find'])
        db = Database(DB_FILE)
        result = find_file_match(db, args['find'])
        print("Result:", result)
