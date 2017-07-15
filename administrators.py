class Admins:
    __path = 'admins_list.dat'

    def __init__(self):
        f = open(self.__path, 'r')
        self.__admins = eval(f.read())
        f.close()

    def add(self, uid, bot):
        user_info = bot.get_chat(chat_id=uid)
        self.__admins[uid] = user_info.username
        self.__update_admins_list()

    def delete(self, uid):
        self.__admins.pop(uid)
        self.__update_admins_list()

    def admins_list(self):
        a_list = 'Administrators list:\n'
        for i in self.__admins.items():
            a_list = a_list + str(i[0]) + ' - @' + i[1] + '\n'
        return a_list

    def is_exist(self, uid):
        return self.__admins.get(uid, False)

    def __update_admins_list(self):
        f = open(self.__path, 'w')
        f.write(repr(self.__admins))
        f.close()
