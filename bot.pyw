"""v.1"""

import config
import telebot
import messages
import os
from time import sleep
from administrators import Admins
import subprocess
import report
import requests


user_step = {}
user_action = {}
bot = telebot.TeleBot(config.token)

# create keyboard
markup = telebot.types.ReplyKeyboardMarkup()
help_btn = telebot.types.KeyboardButton('Help')
music_btn = telebot.types.KeyboardButton('Music')
get_id_btn = telebot.types.KeyboardButton('My id')
state_btn = telebot.types.KeyboardButton("Bot's state")
markup.row(get_id_btn)
markup.row(music_btn)
markup.row(help_btn)
markup.row(state_btn)

admin = Admins()


def get_user_step(uid):
    try:
        return user_step[uid]
    except KeyError:
        user_step[uid] = 0


@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_chat_action(chat_id=message.chat.id, action='typing')
    sleep(1)
    user_info = bot.get_chat(chat_id=message.chat.id)
    first_name = str(user_info.first_name)
    last_name = str(user_info.last_name)
    first_name = first_name.replace('None', '')
    last_name = last_name.replace('None', '')
    message_text = 'Hi, ' + first_name + ' ' + last_name
    bot.send_message(message.chat.id, text=message_text, reply_markup=markup)
    bot.send_message(message.chat.id, messages.start_message, reply_markup=markup)


@bot.message_handler(commands=['help'])
def handle_help(message):
    bot.send_message(message.chat.id, messages.help_message, reply_markup=markup)


@bot.message_handler(commands=['music'])
def handle_music(message):
    bot.send_chat_action(chat_id=message.chat.id, action='typing')
    f = open('Snoop Doog Doors - Riders On The Storm.mp3', 'rb')
    bot.send_audio(chat_id=message.chat.id, audio=f, timeout=999, reply_markup=markup)
    f.close()


@bot.message_handler(commands=['get_id'])
def handle_chat_id(message):
    bot.send_message(chat_id=message.chat.id, text=str(message.chat.id))


@bot.message_handler(commands=['status'])
def handle_status(message):
    bot.send_message(chat_id=message.chat.id, text='Bot is working :)')
    output = subprocess.check_output(['date'])
    bot.send_message(chat_id=message.chat.id, text='Time of server: ' + output.decode('utf-8'))
    if admin.is_exist(message.chat.id):
        output = subprocess.check_output(['ps', '-F', '-C', 'sudo -b python bot.pyw'])
        bot.send_message(chat_id=message.chat.id, text=output)


@bot.message_handler(commands=['admin'])
def handle_admin(message):
    if not admin.is_exist(message.chat.id):
        bot.send_message(chat_id=message.chat.id, text='You are not administrator!')
        return None

    user_action[message.chat.id] = ''
    command = message.text
    command = command.replace('/admin ', '')
    if command.find('stop server') != -1:
        user_action[message.chat.id] = 'stop server'
    elif command.find('reboot server') != -1:
        user_action[message.chat.id] = 'reboot server'
    elif command.find('stop bot') != -1:
        user_action[message.chat.id] = 'stop bot'
    elif command.find('add') != -1:
        uid = command.replace('add ', '')
        admin.add(uid=int(uid), bot=bot)
        bot.send_message(chat_id=message.chat.id, text='Administrator has added')
    elif command.find('delete') != -1:
        uid = command.replace('delete ', '')
        admin.delete(uid=int(uid))
        bot.send_message(chat_id=message.chat.id, text='Administrator has deleted')
    elif command.find('list') != -1:
        a_list = admin.admins_list()
        bot.send_message(chat_id=message.chat.id, text=a_list)
    else:
        bot.send_message(chat_id=message.chat.id, text=messages.admin_command_error)

    if user_action[message.chat.id] != '':
        user_step[message.chat.id] = 1
        bot.send_message(chat_id=message.chat.id, text='Are you sure? (Yes/No)')


@bot.message_handler(func=lambda message: get_user_step(message.chat.id) == 1)
def handle_conformation(message):
    if message.text == 'Yes':
        if user_action[message.chat.id] == 'stop server':
            try:
                os.system('shutdown -P +1')
                bot.send_message(chat_id=message.chat.id, text='Server will shut down in a minute')
            except Exception:
                bot.send_message(chat_id=message.chat.id, text='An error occurred. Try again')
        elif user_action[message.chat.id] == 'reboot server':
            try:
                os.system('shutdown -r +1')
                bot.send_message(chat_id=message.chat.id, text='Server will reboot in a minute')
            except Exception:
                bot.send_message(chat_id=message.chat.id, text='An error occurred. Try again')
        elif user_action[message.chat.id] == 'stop bot':
            bot.send_message(chat_id=message.chat.id, text='Bot has shut down')
            exit(0)
        user_action[message.chat.id] = ''
        user_step[message.chat.id] = 0
    elif message.text == 'No':
        bot.send_message(chat_id=message.chat.id, text='Action cancelled')
        user_action[message.chat.id] = ''
        user_step[message.chat.id] = 0
    else:
        bot.send_message(chat_id=message.chat.id, text='You should type "Yes" or "No"')


@bot.message_handler(func=lambda message: get_user_step(message.chat.id) == 0, content_types=["text"])
def text_command(message):
        if message.text == 'Music':
            handle_music(message)
        elif message.text == 'Help':
            handle_help(message)
        elif message.text == 'My id':
            handle_chat_id(message)
        elif message.text == "Bot's state":
            handle_status(message)
        else:
            bot.send_message(message.chat.id, text="I don't understand you")


if __name__ == '__main__':
    while True:
        try:
            bot.polling(none_stop=True)
        except requests.exceptions.ReadTimeout:
            report.send()
            sleep(15)
