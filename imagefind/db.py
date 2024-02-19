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
    phash6_90: str = ''
    phash6_180: str = ''
    phash6_270: str = ''
    phash8: str = ''
    phash8_90: str = ''
    phash8_180: str = ''
    phash8_270: str = ''
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
                self.conn.row_factory = sqlite3.Row
            except sqlite3.Error as e:
                print(e)
        return self.conn

    # Function to create a table to store file information
    def create_table(self):
        try:
            cursor = self.create_connection().cursor()
            # cursor.execute('DROP TABLE IF EXISTS files')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT,
                    size INTEGER,
                    file_last_modified TEXT,
                    phash_last_modified TEXT
                )
            ''')
        except sqlite3.Error as e:
            print(e)
        self.create_table_add_rotations()

    def create_table_add_rotations(self):
        cols = ['phash6', 'phash8', 'phash10', 'phash12']
        rotations = ['', '_90', '_180', '_270']
        for c in cols:
            for r in rotations:
                try:
                    cursor =self.create_connection().cursor()
                    cursor.execute(f"ALTER TABLE files ADD COLUMN {c}{r} TEXT")
                    print("added column " + c + r + "")
                except sqlite3.Error as e:
                    print(e)

    # Function to insert file information into the database
    def insert_file_info(self, file_data: FileData):
        try:
            cursor = self.create_connection().cursor()

            sql = '''
                INSERT INTO files (filename, size, file_last_modified, phash_last_modified, phash6, phash6_90, phash6_180, phash6_270, phash8, phash10, phash12)
                VALUES (?, ?, ?, ?, ?, ? ,?, ?, ?, ? ,?)
            '''

            cursor.execute(sql, (file_data.filename, file_data.size, file_data.file_last_modified, file_data.phash_last_modified,
                  file_data.phash6, file_data.phash6_90, file_data.phash6_180, file_data.phash6_270, file_data.phash8, file_data.phash10, file_data.phash12))
            self.conn.commit()
        except sqlite3.Error as e:
            print(e)

    def delete_file(self, file_name: str):
        try:
            cursor = self.create_connection().cursor()

            sql = 'DELETE FROM files where filename = ?'

            cursor.execute(sql, (file_name,))
            self.conn.commit()
        except sqlite3.Error as e:
            print(e)


    def row_to_FileData(self, row):
        return FileData(id=row['id'], filename=row['filename'], size=row['size'],
                        file_last_modified=row['file_last_modified'], phash_last_modified=row['phash_last_modified'],
                        phash6=row['phash6'], phash8=row['phash8'], phash10=row['phash10'], phash12=row['phash12'])


    def find_by_file_name(self, file_name: str):
        cursor = self.create_connection().cursor()
        sql = "select * from files where filename = ?"
        cursor.execute(sql, (file_name,))
        rows = cursor.fetchall()
        if len(rows) > 0:
            return self.row_to_FileData(rows[0])
        return None

    def find_by_hash(self, phash6: str):
        cursor = self.create_connection().cursor()
        sql = "select * from files where phash6 = ?"
        cursor.execute(sql, (phash6,))
        rows = cursor.fetchall()
        result = []
        for row in rows:
            fd = self.row_to_FileData(row)
            result.append(self.row_to_FileData(row))
        return result


