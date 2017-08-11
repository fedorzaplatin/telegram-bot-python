import sqlite3
import os
import random
import logging


class Manager:
    __database_name = 'quotes_database.db'

    def __init__(self):
        self.log = logging.getLogger(__name__)
        self.log.setLevel(logging.INFO)

        if not os.path.exists('./databases/' + self.__database_name):
            self.log.info('Database of quotes does not exits')
            self.__create_date_base()
            self.__quotes_list = []
        else:
            self.__conn = sqlite3.connect('./databases/' + self.__database_name, check_same_thread=False)
            self.__cur = self.__conn.cursor()
            self.log.info('Database of quotes was connected')
            self.__cur.execute("SELECT quote FROM quotes_list")
            self.__quotes_list = self.__cur.fetchall()

    def __create_date_base(self):
        self.__conn = sqlite3.connect('./databases/' + self.__database_name, check_same_thread=False)
        self.__cur = self.__conn.cursor()
        self.__cur.execute('CREATE TABLE quotes_list (id INTEGER PRIMARY KEY AUTOINCREMENT, quote TEXT NOT NULL)')
        self.__conn.commit()
        self.log.info('Database of quotes was created and connected')

    def terminate(self):
        self.__conn.close()

    def random(self):
        quote = random.choice(self.__quotes_list)
        quote = quote[0]
        return quote

    def add_new(self, quote):
        self.__cur.execute('INSERT INTO quotes_list (quote) VALUES (?)', [quote])
        self.__conn.commit()
        self.__cur.execute("SELECT quote FROM quotes_list")
        self.__quotes_list = self.__cur.fetchall()

    def delete(self, quote_id):
        self.__cur.execute('DELETE FROM quotes_list WHERE id=?', [quote_id])
        self.__conn.commit()
        self.__cur.execute("SELECT quote FROM quotes_list")
        self.__quotes_list = self.__cur.fetchall()

    def list(self):
        self.__cur.execute('SELECT * FROM quotes_list')
        quotes_list = self.__cur.fetchall()
        return quotes_list


class NoQuotes(Exception):
    pass
