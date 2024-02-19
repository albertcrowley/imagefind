# This is a sample Python script.
# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import multiprocessing
import os
import sys
import time
from functools import partial

import imagehash
import numpy
import numpy as np
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
logger = logging.getLogger("imagefind log")
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


def hash(fname: str, phash_level=6):
    image = Image.open(fname)
    return imagehash.phash(image, phash_level)


def scan_file(db: Database, file_name: str):
    try:
        if db.find_by_file_name(file_name) == None:
            image_hash = hash(file_name, 6)
            size = os.path.getsize(file_name)
            last_modified = time.strftime(DATE_FORMAT, time.localtime(os.path.getmtime(file_name)))

            fd = FileData(filename=file_name, size=size, file_last_modified=last_modified,
                          phash6=image_hash.__str__())
            db.insert_file_info(fd)
            logger.info(fd)
            return 1
    except UnidentifiedImageError:
        logger.error("Unidentified image error for {}".format(file_name))
    except:
        logger.error("Unknown error for {}".format(file_name))
    return 0


def scan(dir_name: str, db: Database, parallel=64):
    start_time = time.time()
    file_list = find_jpeg_files(dir_name)
    count_updated = 0
    # for file_name in tqdm(file_list):
    i = 0
    with tqdm(total=len(file_list)) as pbar:
        while i < len(file_list):
            if i < len(file_list) - (parallel * 2):
                batch = file_list[i:i + parallel]
                with multiprocessing.Pool() as pool:
                    results = pool.map(partial(scan_file, db), batch)
                    count_updated = sum(results)
                    i += parallel
                    pbar.update(parallel)
            else:
                count_updated += scan_file(file_name=file_list[i], db=db)
                i += 1
                pbar.update(1)

    end_time = time.time()
    execution_time = end_time - start_time

    return {'run_time': execution_time, 'files_processed': len(file_list), 'files_updated': count_updated}


def parse_arguments():
    parser = ArgumentParser()
    parser.add_argument("-l", "--log", default='WARN', help="Set log level, choose one of DEBUG, INFO, WARN, ERROR")
    parser.add_argument("-d", "--dir", default=None, help="Directory to use as the base of the scan")
    parser.add_argument("-f", "--find", default=None, help="File to find")
    parser.add_argument("-6", "--phash6", default=None, help="caluclate phash6 of the supplied file")
    parser.add_argument("--d1", default=None, help="File 1 for difference")
    parser.add_argument("--d2", default=None, help="File 2 for difference")
    # parser.add_argument("-8", "--phash8", default=None, help="caluclate phash8 of the supplied file")
    # parser.add_argument("-10", "--phash10", default=None, help="caluclate phash10 of the supplied file")
    # parser.add_argument("-12", "--phash12", default=None, help="caluclate phash12 of the supplied file")
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

    if args['dir'] is not None:
        logger.info("Scanning " + args['dir'])
        db = Database(DB_FILE)
        runtime = scan(args['dir'], db)
        print("Execution time:", runtime)

    if args['find'] is not None:
        logger.info("Looking for  " + args['find'])
        db = Database(DB_FILE)
        result = find_file_match(db, args['find'])
        print("Result:", result)

    if args['phash6'] is not None:
        # h = imagehash.crop_resistant_hash( Image.open(args['phash6']) )

        h: imagehash.ImageHash
        # h = imagehash.colorhash(Image.open(args['phash6']), 4)
        i = Image.open(args['phash6'])
        i.save('sane.png')
        h = imagehash.phash(i, 4)
        print (h)
        npa = np.array(h.hash)
        print(npa.astype(int))

    if args['d1'] is not None and args['d2'] is not None:
        level = 8
        h1 = imagehash.dhash(Image.open(args['d1']), level)
        h2 = imagehash.dhash(Image.open(args['d2']), level)
        print(h1)
        print(h2)

        n1 = (np.array(h1.hash)).astype(int)
        n2 = (np.array(h2.hash)).astype(int)

        print (n1)
        print()
        print (n2)
        print()
        print( np.absolute( n1-n2 ))
        print ("total bits " + (np.sum (np.absolute( n1-n2 ))).__str__())

