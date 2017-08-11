import sqlite3
import os
import random


class Manager:
    __database_name = 'quotes_database.db'

    def __init__(self):
        if not os.path.exists('./databases/' + self.__database_name):
            self.__create_date_base()
        else:
            self.__conn = sqlite3.connect('./databases/' + self.__database_name, check_same_thread=False)
            self.__cur = self.__conn.cursor()
            self.__cur.execute('SELECT count FROM info_table WHERE parameter="quotes_count"')
            self.__quotes_count = self.__cur.fetchall()
            self.__quotes_count = self.__quotes_count[0][0]

    def __create_date_base(self):
        self.__conn = sqlite3.connect(self.__database_name, check_same_thread=False)
        self.__cur = self.__conn.cursor()
        self.__cur.execute('CREATE TABLE quotes_list (num INTEGER PRIMARY KEY AUTOINCREMENT, quote TEXT NOT NULL)')
        self.__cur.execute('CREATE TABLE info_table (_id INTEGER PRIMARY KEY AUTOINCREMENT, parameter TEXT NOT NULL, count INTEGER NOT NULL)')
        self.__cur.execute('INSERT INTO info_table VALUES (1, "quotes_count", 0)')
        self.__conn.commit()
        self.__quotes_count = 0

    def random(self):
        num = random.randint(1, self.__quotes_count)
        self.__cur.execute('SELECT quote FROM quotes_list WHERE num=?', [num])
        quote = self.__cur.fetchall()
        quote = quote[0][0]
        return quote

    def add_new(self, quote):
        self.__cur.execute('SELECT * FROM quotes_list ORDER BY num DESC LIMIT 1')
        num = self.__cur.fetchall()
        num = num[0][0]
        num += 1
        self.__cur.execute('INSERT INTO quotes_list VALUES (?, ?)', [num, quote])
        self.__quotes_count += 1
        self.__cur.execute('UPDATE info_table SET count=count+1 WHERE parameter="quotes_count"')
        self.__conn.commit()
