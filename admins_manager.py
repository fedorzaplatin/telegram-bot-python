import sqlite3
import os
import logging
import configparser


class Manager:
    __database_name = 'bot_database.db'

    def __init__(self, bot):
        self.log = logging.getLogger(__name__)
        self.log.setLevel(logging.INFO)

        self.__bot = bot
        self.__config = configparser.ConfigParser()
        self.__config.read('bot_config.ini')

        if not os.path.exists('./databases/' + self.__database_name):
            self.log.info('Database of admins does not exist')
            self.__create_data_base()
        else:
            self.__conn = sqlite3.connect('./databases/' + self.__database_name, check_same_thread=False)
            self.__cur = self.__conn.cursor()
            self.log.info('Database of admins was connected')

    def __create_data_base(self):
        self.__conn = sqlite3.connect('./databases/' + self.__database_name, check_same_thread=False)
        self.__cur = self.__conn.cursor()
        self.__cur.execute('CREATE TABLE admins_list (user_id INTEGER PRIMARY KEY, '
                           'username TEXT NULL, '
                           'first_name TEXT NOT NULL, '
                           'last_name TEXT NULL, '
                           'notification_on_start INTEGER NOT NULL,'
                           'rloa INTEGER NOT NULL,'  # Can admin read list of admins
                           'eloa INTEGER NOT NULL,'  # Can admin edit list of admins (add, remove and etc.)
                           'eloq INTEGER NOT NULL,'  # Can admin edit list of quotes
                           'emc INTEGER NOT NULL,'  # Can admin edit command /music
                           'sb INTEGER NOT NULL)')  # Can admin stop bot
        user_info = self.__bot.get_chat(self.__config.getint('MAIN ADMIN', 'user_id'))
        self.add(user_info)
        self.__cur.execute("UPDATE admins_list SET rloa=1, eloa=1, eloq=1, emc=1, sb=1 WHERE user_id=?",
                           [user_info.id])
        self.__conn.commit()
        self.log.info('Database of admins was created and connected')

    def terminate(self):
        self.__conn.close()
        self.log.info('Admin db was disconnected')

    def add(self, user_info):
        self.__cur.execute("INSERT INTO admins_list"
                           "(user_id, first_name, notification_on_start, rloa, eloa, eloq, emc, sb)"
                           "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                           [user_info.id, user_info.first_name, 0, 0, 0, 0, 0, 0])
        if user_info.username:
            self.__cur.execute("UPDATE admins_list SET username=? WHERE user_id=?",
                               [user_info.username, user_info.id])
        if user_info.last_name:
            self.__cur.execute("UPDATE admins_list SET last_name=? WHERE user_id=?",
                               [user_info.last_name, user_info.id])
        self.__conn.commit()
        self.log.debug('Admin ({}, {}) was added'.format(user_info.id, user_info.first_name))

    def delete(self, user_id):
        if user_id == self.__config.getint('MAIN ADMIN', 'user_id'):
            raise NotEnoughPermissions('You cant remove the main admin')
        self.__cur.execute("DELETE FROM admins_list WHERE user_id=?", [user_id])
        self.__conn.commit()

    def list(self):
        self.log.debug('List of administrators was requested')
        self.__cur.execute("SELECT * FROM admins_list")
        admin_list = self.__cur.fetchall()
        return admin_list

    def is_admin(self, user_id):
        self.__cur.execute("SELECT username FROM admins_list WHERE user_id=?", [user_id])
        user = self.__cur.fetchall()
        return len(user) == 1

    def check_permission(self, user_id, flag):
        self.__cur.execute("SELECT ? FROM admins_list WHERE user_id=?", [flag, user_id])
        result = self.__cur.fetchall()
        return result[0][0]

    def edit_permissions(self, initiator, user_id, exp):
        if not self.check_permission(initiator, 'eloa'):
            raise NotEnoughPermissions('You cant edit permissions of administrators')

        permissions = exp.split()
        for perm in permissions:
            if perm[0] == '+':
                self.__cur.execute("UPDATE admins_list SET ?=1 WHERE user_id=?", [perm[1:], user_id])
            else:
                self.__cur.execute("UPDATE admins_list SET ?=0 WHERE user_id=?", [perm[1:], user_id])
        self.__conn.commit()
        self.log.info('Admin {} has edited permissions of admin {}'.format(self.text_info(initiator),
                                                                           self.text_info(user_id)))

    def notif(self, user_id):
        self.__cur.execute("SELECT notification_on_start FROM admins_list WHERE user_id=?", [user_id])
        status = self.__cur.fetchall()
        status = status[0][0]
        return status == 1

    def disable_notification(self, user_id):
        self.__cur.execute("UPDATE admins_list SET notification_on_start=0 WHERE user_id=?", [user_id])
        self.__conn.commit()

    def enable_notification(self, user_id):
        self.__cur.execute("UPDATE admins_list SET notification_on_start=1 WHERE user_id=?", [user_id])
        self.__conn.commit()

    def notification_list(self):
        self.__cur.execute("SELECT user_id FROM admins_list WHERE notification_on_start=1")
        tmp = self.__cur.fetchall()
        l = []
        for i in tmp:
            l.append(i[0])
        return l

    def update_info(self):
        self.log.debug('Beginning updating information')
        self.__cur.execute("SELECT user_id FROM admins_list")
        admins_list = self.__cur.fetchall()

        for admin in admins_list:
            self.log.debug('Updating info about ' + str(admin[0]))
            admin_info = self.__bot.get_chat(admin[0])
            self.__cur.execute("UPDATE admins_list SET first_name=? WHERE user_id=?", [admin_info.first_name, admin[0]])
            if admin_info.username:
                self.__cur.execute("UPDATE admins_list SET username=? WHERE user_id=?", [admin_info.username, admin[0]])
            if admin_info.last_name:
                self.__cur.execute("UPDATE admins_list SET last_name=? WHERE user_id=?",
                                   [admin_info.last_name, admin[0]])
        self.__conn.commit()
        self.log.debug('Information about admins successfully updated')

    def info(self, user_id):
        self.__cur.execute('SELECT * FROM admins_list WHERE user_id=?', [user_id])
        admin_info = self.__cur.fetchall()
        admin_info = admin_info[0]
        return admin_info

    def text_info(self, user_id):
        admin_info = self.info(user_id)
        text = admin_info[2]
        if admin_info[3]:
            text += ' ' + admin_info[3]
        text += ' (' + str(admin_info[0])
        if admin_info[1]:
            text += ' @' + admin_info[1]
        text += ')'
        return text


class AdminIdError(Exception):
    pass


class NotEnoughPermissions(Exception):
    pass
