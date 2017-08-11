import sqlite3
import os


class Manager:
    __database_name = 'bot_database.db'

    def __init__(self):
        if not os.path.exists('./databases/' + self.__database_name):
            self.__create_date_base()
        else:
            self.__conn = sqlite3.connect('./databases/' + self.__database_name, check_same_thread=False)
            self.__cur = self.__conn.cursor()

    def __create_date_base(self):
        self.__conn = sqlite3.connect(self.__database_name, check_same_thread=False)
        self.__cur = self.__conn.cursor()
        self.__cur.execute('CREATE TABLE admins_list (user_id INTEGER PRIMARY KEY AUTOINCREMENT, '
                           'username TEXT NOT NULL, '
                           'first_name TEXT NULL, '
                           'last_name TEXT NULL, '
                           'notification_on_start INTEGER NOT NULL)')
        self.__conn.commit()

    def add(self, user_info):
        user_info_list = [user_info.id, user_info.username, user_info.first_name, user_info.last_name, 1]
        self.__cur.execute("INSERT INTO admins_list VALUES (?, ?, ?, ?, ?)", user_info_list)
        self.__conn.commit()

    def delete_admin(self, username=None):
        self.__cur.execute("DELETE FROM admins_list WHERE username=?", [username])
        self.__conn.commit()

    def list(self):
        self.__cur.execute("SELECT * FROM admins_list")
        admin_list = self.__cur.fetchall()
        message = 'Administrators list:\n'
        for admin in admin_list:
            message += '@{} - {} {}\n'.format(admin[1], admin[2], admin[3])
        return message

    def is_admin(self, uid):
        self.__cur.execute("SELECT username FROM admins_list WHERE user_id=?", [uid])
        user = self.__cur.fetchall()
        if len(user) == 1:
            return True
        else:
            return False

    def is_notification_on(self, uid):
        self.__cur.execute("SELECT notification_on_start FROM admins_list WHERE user_id=?", [uid])
        status = self.__cur.fetchall()
        status = status[0][0]
        if status == 1:
            return True
        else:
            return False

    def disable_notification(self, uid):
        self.__cur.execute("UPDATE admins_list SET notification_on_start=0 WHERE user_id=?", [uid])
        self.__conn.commit()

    def enable_notification(self, uid):
        self.__cur.execute("UPDATE admins_list SET notification_on_start=1 WHERE user_id=?", [uid])
        self.__conn.commit()

    def notification_list(self):
        self.__cur.execute("SELECT user_id FROM admins_list WHERE notification_on_start=1")
        tmp = self.__cur.fetchall()
        l = []
        for i in tmp:
            l.append(i[0])
        return l
