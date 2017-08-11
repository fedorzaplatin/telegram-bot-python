"""v.2"""

from time import sleep
import os
import subprocess
from configparser import ConfigParser

import telebot

import admins_manager
import messages
import quotes_manager
import keyboards

bot_config = ConfigParser()
bot_config.read('bot_config.ini')
user_step = {}
user_action = {}
bot = telebot.TeleBot(bot_config.get('DEFAULT', 'token'))
admin = admins_manager.Manager()
quote = quotes_manager.Manager()

user_keyboard = keyboards.main('user')
admin_keyboard = keyboards.main('admin')


def get_user_step(uid):
    try:
        return user_step[uid]
    except KeyError:
        user_step[uid] = 0


@bot.message_handler(commands=['start'])
def handle_start(message):
    user_step[message.chat.id] = 0
    bot.send_chat_action(chat_id=message.chat.id, action='typing')
    sleep(1)
    user_info = bot.get_chat(chat_id=message.chat.id)
    first_name = str(user_info.first_name)
    last_name = str(user_info.last_name)
    first_name = first_name.replace('None', '')
    last_name = last_name.replace('None', '')
    message_text = 'Привет, ' + first_name + ' ' + last_name
    bot.send_message(message.chat.id, text=message_text)
    if admin.is_admin(message.chat.id):
        bot.send_message(message.chat.id, messages.start_message, reply_markup=admin_keyboard)
    else:
        bot.send_message(message.chat.id, messages.start_message, reply_markup=user_keyboard)


@bot.message_handler(commands=['help'])
def handle_help(message):
    bot.send_message(message.chat.id, messages.help_message)


@bot.message_handler(commands=['music'])
def handle_music(message):
    bot.send_chat_action(chat_id=message.chat.id, action='typing')
    f = open('./files/Sekai - She Came Back (Kill The Copyright Release).mp3', 'rb')
    bot.send_audio(chat_id=message.chat.id, audio=f, timeout=999)
    f.close()


@bot.message_handler(commands=['get_id'])
def handle_chat_id(message):
    bot.send_message(chat_id=message.chat.id, text=str(message.chat.id))


@bot.message_handler(commands=['status'])
def handle_status(message):
    bot.send_message(chat_id=message.chat.id, text='The bot is working :)')
    output = subprocess.check_output(['date'])
    bot.send_message(chat_id=message.chat.id, text='Time of the server: ' + output.decode('utf-8'))
    if admin.is_admin(message.chat.id):
        output = subprocess.check_output(['ps', '-F', '-C', 'sudo -b python bot.pyw'])
        bot.send_message(chat_id=message.chat.id, text=output)


@bot.message_handler(commands=['admin'])
def handle_admin(message):
    if not admin.is_admin(message.chat.id):
        bot.send_message(chat_id=message.chat.id, text='You are not administrator!')
        return None

    user_action[message.chat.id] = ''
    command = message.text
    command = command.replace('/admin ', '')
    if command.find('stop server') != -1:
        user_action[message.chat.id] = 'stop server'
        bot.register_next_step_handler(message, action_conformation)
    elif command.find('reboot server') != -1:
        user_action[message.chat.id] = 'reboot server'
        bot.register_next_step_handler(message, action_conformation)
    elif command.find('stop bot') != -1:
        user_action[message.chat.id] = 'stop bot'
        bot.register_next_step_handler(message, action_conformation)
    elif command.find('add') != -1:
        bot.send_message(message.chat.id, 'Forward a message of the user who you want to make an administrator to me')
        bot.register_next_step_handler(message, new_admin)
    elif command.find('delete') != -1:
        bot.send_message(message.chat.id, admin.list())
        bot.send_message(message.chat.id,
                         'Send me an user name (without "@") of the user you want to remove from administrators list')
        bot.register_next_step_handler(message, delete_admin)
    elif command.find('list') != -1:
        a_list = admin.list()
        bot.send_message(chat_id=message.chat.id, text=a_list)
        return None
    else:
        bot.send_message(chat_id=message.chat.id, text=messages.admin_command_error)
        return None

    user_step[message.chat.id] = 1
    if user_action[message.chat.id]:
        markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add('OK', 'Cancel')
        bot.send_message(message.chat.id, 'Confirm the action', reply_markup=markup)


def new_admin(message):
    first_name = str(message.forward_from.first_name)
    last_name = str(message.forward_from.last_name)
    user_name = '@' + message.forward_from.username
    name = first_name.replace('None', '') + ' ' + last_name.replace('None', '')
    text = 'The user {} ({}) will be made administrator'.format(name, user_name)
    bot.send_message(message.chat.id, text)
    user_action[message.chat.id] = {'action': 'add', 'param': message.forward_from}
    markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add('OK', 'Cancel')
    bot.send_message(message.chat.id, 'Confirm the action', reply_markup=markup)
    bot.register_next_step_handler(message, action_conformation)


def delete_admin(message):
    user_action[message.chat.id] = {'action': 'delete', 'param': message.text}
    text = 'The user {} will be removed from administrators list'.format(message.text)
    bot.send_message(message.chat.id, text)
    markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add('OK', 'Cancel')
    bot.send_message(message.chat.id, 'Confirm the action', reply_markup=markup)
    bot.register_next_step_handler(message, action_conformation)


def action_conformation(message):
    if message.text == 'Продолжить':
        if user_action[message.chat.id] == 'stop server':
            os.system('shutdown -P +1')
            bot.send_message(chat_id=message.chat.id,
                             text='The server will be shut down in a minute',
                             reply_markup=admin_keyboard)
        elif user_action[message.chat.id] == 'reboot server':
            os.system('shutdown -r +1')
            bot.send_message(chat_id=message.chat.id,
                             text='The server will reboot in a minute',
                             reply_markup=admin_keyboard)
        elif user_action[message.chat.id] == 'stop bot':
            bot.send_message(chat_id=message.chat.id,
                             text='The bot has shut down',
                             reply_markup=admin_keyboard)
            exit(0)
        elif user_action[message.chat.id]['action'] == 'add':
            admin.add(user_action[message.chat.id]['param'])
            bot.send_message(message.chat.id, 'A new administrator has added')
        elif user_action[message.chat.id]['action'] == 'delete':
            admin.delete_admin(user_action[message.chat.id]['param'])
            bot.send_message(message.chat.id, 'The administrator has deleted')
        user_action[message.chat.id] = ''
    elif message.text == 'Отмена':
        bot.send_message(chat_id=message.chat.id, text='Action cancelled')
        user_action[message.chat.id] = ''
    bot.send_message(message.chat.id, 'Main menu', reply_markup=admin_keyboard)
    user_step[message.chat.id] = 0


@bot.message_handler(commands=['setting'])
def handle_setting(message):
    user_step[message.chat.id] = 1  # disabling main menu handler
    notifications = admin.is_notification_on(message.chat.id)
    bot.send_message(message.chat.id, "Settings", reply_markup=keyboards.setting(notifications))
    bot.register_next_step_handler(message, setting_menu)


def setting_menu(message):
    if message.text == 'Add a new quote':
        bot.register_next_step_handler(message, add_new_quote)
        bot.send_message(message.chat.id, 'Send me a quote in following format:\n'
                                          '[Quote]\n\n'
                                          '[Author]/Unknown author')
    elif message.text == 'Disable notifications':
        admin.disable_notification(message.chat.id)
        notifications = admin.is_notification_on(message.chat.id)
        bot.send_message(message.chat.id, 'Notifications have disabled', reply_markup=keyboards.setting(notifications))
        bot.register_next_step_handler(message, setting_menu)
    elif message.text == 'Enable notifications':
        admin.enable_notification(message.chat.id)
        notifications = admin.is_notification_on(message.chat.id)
        bot.send_message(message.chat.id, 'Notifications have enabled', reply_markup=keyboards.setting(notifications))
        bot.register_next_step_handler(message, setting_menu)
    elif message.text == 'Back':
        if admin.is_admin(message.chat.id):
            bot.send_message(message.chat.id, 'Main menu', reply_markup=admin_keyboard)
        else:
            bot.send_message(message.chat.id, 'Main menu', reply_markup=user_keyboard)
        user_step[message.chat.id] = 0


def add_new_quote(message):
    quote.add_new(message.text)
    bot.send_message(message.chat.id, 'The quote has added')
    bot.register_next_step_handler(message, handle_setting)


# main menu handler
@bot.message_handler(func=lambda message: get_user_step(message.chat.id) == 0, content_types=["text"])
def text_command(message):
        if message.text == 'Music':
            handle_music(message)
        elif message.text == 'Help':
            handle_help(message)
        elif message.text == 'My ID':
            handle_chat_id(message)
        elif message.text == "Bot's state":
            handle_status(message)
        elif message.text == 'Random quote':
            bot.send_message(chat_id=message.chat.id, text=quote.random())
        elif message.text == 'Settings' and admin.is_admin(message.chat.id):
            handle_setting(message)
        else:
            bot.send_message(message.chat.id, text='There is no such commands')


if __name__ == '__main__':
    bot.polling(none_stop=True)
    notification_list = admin.notification_list()
    for user_id in notification_list:
        bot.send_message(user_id, 'Бот включён')
