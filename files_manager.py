import sqlite3
import os
import logging


class Manager:
    __database_name = 'files_database.db'

    def __init__(self):
        self.log = logging.getLogger(__name__)
        self.log.setLevel(logging.INFO)

        if not os.path.exists('./databases/' + self.__database_name):
            self.log.info('Database of files does not exist')
            self.__create_date_base()
        else:
            self.__conn = sqlite3.connect('./databases/' + self.__database_name, check_same_thread=False)
            self.__cur = self.__conn.cursor()
            self.log.info('Database of files was connected')

    def __create_date_base(self):
        self.__conn = sqlite3.connect('./databases/' + self.__database_name, check_same_thread=False)
        self.__cur = self.__conn.cursor()
        self.__cur.execute('CREATE TABLE files_list (file_id TEXT PRIMARY KEY, '
                           'file_name TEXT NOT NULL)')
        self.__conn.commit()
        self.log.info('Database of files was created and connected')

    def terminate(self):
        self.__conn.close()

    def get_id(self, file_name):
        self.__cur.execute("SELECT file_id FROM files_list WHERE file_name=?", [file_name])
        file_id = self.__cur.fetchall()
        if len(file_id) == 0:
            raise FileNameError('There is no such file_name ({}) in database'.format(file_name))
        else:
            return file_id[0][0]

    def add(self, file_name, file_id):
        self.__cur.execute("INSERT INTO files_list VALUES (?, ?)", [file_id, file_name])
        self.__conn.commit()

    def delete(self, file_id=None, file_name=None):
        if not file_name and not file_id:
            raise SyntaxError('The method must take at least one argument')
        if file_id:
            self.__cur.execute("DELETE FROM files_list WHERE file_id=?", [file_id])
        else:
            self.__cur.execute("DELETE FROM files_list WHERE file_name=?", [file_name])
        self.__conn.commit()

    def list(self):
        self.log.debug('List of files was requested')
        self.__cur.execute("SELECT * FROM files_list")
        return self.__cur.fetchall()


class FileNameError(Exception):
    pass
