import sqlite3
import os
import time
from datetime import datetime

from dataclasses import dataclass, field

DATE_FORMAT = '%Y-%m-%d %H:%M:%S'


def current_time():
    return datetime.now().strftime(DATE_FORMAT)



@dataclass
class FileData:
    filename: str
    size: int
    id: int = 0
    file_last_modified: str = field(default_factory=current_time)
    phash_last_modified: str = field(default_factory=current_time)
    phash6: str = ''
    phash8: str = ''
    phash10: str = ''
    phash12: str = ''


class Database:

    conn = None
    db_file = None

    def __init__(self, database_file: str):
        self.db_file = database_file

    def __del__(self):
        if self.conn is not None:
            self.conn.close()

    # Function to create a SQLite database connection
    def create_connection(self):
        if self.conn is None:
            try:
                self.conn = sqlite3.connect(self.db_file)
            except sqlite3.Error as e:
                print(e)
        return self.conn

    # Function to create a table to store file information
    def create_table(self):
        try:
            cursor = self.create_connection().cursor()
            cursor.execute('DROP TABLE IF EXISTS files')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT,
                    size INTEGER,
                    file_last_modified TEXT,
                    phash_last_modified TEXT,
                    phash6 TEXT,
                    phash8 TEXT,
                    phash10 TEXT,
                    phash12 TEXT
                )
            ''')
        except sqlite3.Error as e:
            print(e)

    # Function to insert file information into the database
    def insert_file_info(self, file_data: FileData):
        try:
            cursor = self.create_connection().cursor()

            sql = '''
                INSERT INTO files (filename, size, file_last_modified, phash_last_modified, phash6, phash8, phash10, phash12)
                VALUES (?, ?, ?, ?, ?, ? ,?, ?)
            '''

            cursor.execute(sql, (file_data.filename, 777, file_data.file_last_modified, file_data.phash_last_modified,
                  file_data.phash6, file_data.phash8, "hithere", file_data.phash12))
            self.conn.commit()
        except sqlite3.Error as e:
            print(e)




