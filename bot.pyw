import os
from configparser import ConfigParser
import logging

import telebot

import admins_manager
import messages
import quotes_manager
import keyboards
import files_manager
import service_functions


release_date = '11.08.2017'
version = '4'
logging.basicConfig(filename='log.log',
                    format='%(filename)s[LINE:%(lineno)d] %(levelname)-8s [%(asctime)s]  %(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
bot_config = ConfigParser()
bot_config.read('bot_config.ini')

log.info('Telegram authentication')
bot = telebot.TeleBot(bot_config.get('DEFAULT', 'token'))
user_action = {}
admin = admins_manager.Manager(bot)
quote = quotes_manager.Manager()
file = files_manager.Manager()
remove_keyboard = telebot.types.ReplyKeyboardRemove()

if bot_config.getboolean('DEFAULT', 'debug'):
    log.setLevel(logging.DEBUG)
    admin.log.setLevel(logging.DEBUG)
    file.log.setLevel(logging.DEBUG)
    quote.log.setLevel(logging.DEBUG)


def stop_bot(chat_id):
    bot.send_message(chat_id, 'Bot has shut down')
    file.terminate()
    admin.terminate()
    quote.terminate()
    exit(0)


@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_chat_action(message.chat.id, action='typing')

    user_info = bot.get_chat(message.chat.id)
    name = user_info.first_name
    if user_info.last_name:
        name += ' ' + user_info.last_name
    bot.send_message(message.chat.id, 'Hi, {}'.format(name), reply_markup=remove_keyboard)
    bot.send_message(message.chat.id, messages.start_message)


@bot.message_handler(commands=['help'])
def handle_help(message):
    bot.send_message(message.chat.id, messages.help_message)


@bot.message_handler(commands=['music'])
def handle_music(message):
    audios = os.listdir('./music')
    for audio in audios:
        bot.send_chat_action(message.chat.id, action='upload_audio')
        try:
            file_id = file.get_id(audio)
            bot.send_audio(message.chat.id, file_id, timeout=999)
        except (files_manager.FileNameError, telebot.apihelper.ApiException):
            audio_file = open('./music/' + audio, 'rb')
            msg_info = bot.send_audio(message.chat.id, audio_file, timeout=999)
            audio_file.close()
            file.add(audio, msg_info.audio.file_id)


@bot.message_handler(commands=['quote'])
def handle_quote(message):
    bot.send_message(message.chat.id, quote.random())


@bot.message_handler(commands=['get_id'])
def handle_chat_id(message):
    bot.send_message(message.chat.id, str(message.chat.id))


@bot.message_handler(commands=['status'])
def handle_status(message):
    text = 'Bot is running.\n' \
           'Version {}. Build: {}.\n'.format(version, release_date)
    if bot_config.getboolean('DEFAULT', 'test_version'):
        text += 'Status: testing.'
    else:
        text += 'Status: stable.'
    bot.send_message(message.chat.id, text)


@bot.message_handler(commands=['admin'])
def handle_admin(message):
    if not admin.is_admin(message.chat.id):
        bot.send_message(message.chat.id, 'You are not administrator')
        return None

    user_action[message.chat.id] = ''
    command = message.text
    command = command.replace('/admin ', '')
    if command.find('stop bot') != -1:
        user_action[message.chat.id] = 'stop bot'
        bot.register_next_step_handler(message, action_conformation)
    elif command.find('add') != -1:
        keyboard = telebot.types.ReplyKeyboardMarkup()
        keyboard.add('Back')
        bot.send_message(message.chat.id,
                         'Forward a message of the user who you want to make an administrator to me',
                         reply_markup=keyboard)
        bot.register_next_step_handler(message, new_admin)
    elif command.find('delete') != -1:
        admins_list = admin.list()
        msg = service_functions.list_to_text(admins_list)
        bot.send_message(message.chat.id, msg)
        keyboard = telebot.types.ReplyKeyboardMarkup()
        keyboard.add('Назад')
        bot.send_message(message.chat.id,
                         'Send me the number of an administrator you want to delete',
                         reply_markup=keyboard)
        bot.register_next_step_handler(message, delete_admin)
    elif command.find('list') != -1:
        admins_list = admin.list()
        bot.send_message(message.chat.id, service_functions.list_to_text(admins_list))
        return None
    elif command.find('update info') != -1:
        admin.update_info()
        bot.send_message(message.chat.id, 'Information has updated')
        return None
    else:
        bot.send_message(message.chat.id, messages.admin_command_usage)
        return None

    if user_action[message.chat.id]:
        bot.send_message(message.chat.id, 'Confirm the action (y/n)')


def new_admin(message):
    if message.text == 'Назад':
        bot.send_message(message.chat.id, 'Main menu', reply_markup=remove_keyboard)
        return
    try:
        name = str(message.forward_from.first_name)
    except AttributeError:
        bot.send_message(message.chat.id, 'Forward a message of the user who you want to make an administrator to me')
        bot.register_next_step_handler(message, new_admin)
        return

    if message.forward_from.last_name:
        name += ' ' + str(message.forward_from.last_name)
    text = 'The user {} will be made administrator'.format(name)
    bot.send_message(message.chat.id, text)
    user_action[message.chat.id] = {'action': 'add', 'param': message.forward_from}
    bot.send_message(message.chat.id, 'Confirm the action (y/n)')
    bot.register_next_step_handler(message, action_conformation)


def delete_admin(message):
    if message.text == 'Назад':
        bot.send_message(message.chat.id, 'Main menu', reply_markup=remove_keyboard)
        return
    admins_list = admin.list()
    try:
        a = admins_list[int(message.text) - 1][0]
    except (ValueError, TypeError):
        bot.send_message(message.chat.id, 'Send me a NUMBER')
        bot.register_next_step_handler(message, delete_admin)
        return
    except IndexError:
        bot.send_message(message.chat.id, 'There is no such number')
        bot.register_next_step_handler(message, delete_admin)
        return
    user_action[message.chat.id] = {'action': 'delete', 'param': a}
    text = 'The user {} will be deleted from administrators list'.format(admin.text_info(a))
    bot.send_message(message.chat.id, text)
    bot.send_message(message.chat.id, 'Confirm the action (y/n)')
    bot.register_next_step_handler(message, action_conformation)


def action_conformation(message):
    if message.text == 'y' or message.text == 'д':
        if user_action[message.chat.id] == 'stop bot':
            log.info('Admin {} has stopped bot'.format(admin.text_info(message.chat.id)))
            stop_bot(message.chat.id)
        elif user_action[message.chat.id]['action'] == 'add':
            admin.add(user_action[message.chat.id]['param'])
            bot.send_message(message.chat.id, 'A new administrator has added')
            log.info('Admin {} has added new admin {}'.format(admin.text_info(message.chat.id),
                                                              admin.text_info(user_action[message.chat.id]['param'].id)))
        elif user_action[message.chat.id]['action'] == 'delete':
            try:
                admin.delete(user_action[message.chat.id]['param'])
            except admins_manager.NotEnoughPermissions:
                bot.send_message(message.chat.id, 'You have no enough permissions')
            else:
                bot.send_message(message.chat.id, 'The administrator had deleted')
                log.info('Admin {} has deleted admin {}'.format(admin.text_info(message.chat.id),
                                                                admin.text_info(user_action[message.chat.id]['param'])))
        user_action[message.chat.id] = ''
    elif message.text == 'n' or message.text == 'н':
        bot.send_message(message.chat.id, 'The action canceled')
        user_action[message.chat.id] = ''
    else:
        bot.send_message(message.chat.id, 'Type "y" (yes) or "n" (no)')
        bot.register_next_step_handler(message, action_conformation)


@bot.message_handler(commands=['settings'])
def handle_setting(message):
    if not admin.is_admin(message.chat.id):
        bot.send_message(message.chat.id, 'You are not administrator')
        return

    bot.send_message(message.chat.id, 'Settings',
                     reply_markup=keyboards.setting(admin.notif(message.chat.id)))
    bot.register_next_step_handler(message, setting_menu)


def setting_menu(message):
    if message.text == 'Add a new quote':
        bot.send_message(message.chat.id, 'Send me a quote in following format:\n'
                                          '[Quote]\n\n'
                                          '[Author]/Unknown author')
        keyboard = telebot.types.ReplyKeyboardMarkup()
        keyboard.add('Back')
        bot.register_next_step_handler(message, add_new_quote)
    elif message.text == 'Edit quotes list':
        quotes_list = quote.list()
        msg = 'Quotes list:\n'
        for q in quotes_list:
            msg += '{}. {}...\n'.format(q[0], q[1][:15].replace('\n', '  '))
        bot.send_message(message.chat.id, msg)
        keyboard = telebot.types.ReplyKeyboardMarkup()
        keyboard.add('Back')
        bot.send_message(message.chat.id, "Send me a quotes's number you want to delete", reply_markup=keyboard)
        bot.register_next_step_handler(message, delete_quote)
    elif message.text == 'Edit command "music"':
        keyboard = telebot.types.ReplyKeyboardMarkup()
        keyboard.add('Finish')
        bot.send_message(message.chat.id,
                         "Send me a music you want to add to the command\n"
                         "OR\n"
                         "Send me a music's number you want to delete from the command",
                         reply_markup=keyboard)
        audio_files_list = file.list()
        user_action[message.chat.id] = {'action': 'edit music command', 'param': audio_files_list}
        bot.send_message(message.chat.id,
                         service_functions.audio_list_to_text(user_action[message.chat.id]['param']))
        bot.register_next_step_handler(message, edit_music)
    elif message.text == 'Disable notifications':
        admin.disable_notification(message.chat.id)
        bot.send_message(message.chat.id, 'Notifications have disabled',
                         reply_markup=keyboards.setting(admin.notif(message.chat.id)))
        bot.register_next_step_handler(message, setting_menu)
    elif message.text == 'Enable notifications':
        admin.enable_notification(message.chat.id)
        notifications = admin.notif(message.chat.id)
        bot.send_message(message.chat.id, 'Notifications have enabled', reply_markup=keyboards.setting(notifications))
        bot.register_next_step_handler(message, setting_menu)
    elif message.text == 'Back':
        bot.send_message(message.chat.id, 'Main menu', reply_markup=remove_keyboard)


def add_new_quote(message):
    if message.text == 'Back':
        bot.send_message(message.chat.id, 'Main menu', reply_markup=remove_keyboard)
    else:
        quote.add_new(message.text)
        bot.send_message(message.chat.id, 'The quote has added')
        bot.register_next_step_handler(message, handle_setting)


def delete_quote(message):
    if message.text == 'Back':
        bot.register_next_step_handler(message, handle_setting)
        bot.send_message(message.chat.id, 'Main menu', reply_markup=remove_keyboard)
    else:
        quote.delete(int(message.text))
        bot.send_message(message.chat.id, 'The quote has deleted')
        bot.register_next_step_handler(message, delete_quote)


def edit_music(message):
    if message.text == 'Finish':
        bot.send_message(message.chat.id, 'Main menu', reply_markup=remove_keyboard)
        handle_setting(message)
        return

    audio_files_list = user_action[message.chat.id]['param']
    if message.audio:
        bot.send_message(message.chat.id, 'Uploading file, please wait...')
        file_info = bot.get_file(message.audio.file_id)
        file_name = '{} - {}.mp3'.format(message.audio.performer, message.audio.title)
        translate_table = str.maketrans('', '', '\/:*?"<>|')
        file_name.translate(translate_table)
        downloaded_file = bot.download_file(file_info.file_path)
        new_file = open('./music/' + file_name, 'wb')
        new_file.write(downloaded_file)
        new_file.close()
        file.add(file_name, message.audio.file_id)
        bot.send_message(message.chat.id,
                         'Uploading has finished!')
        user_action[message.chat.id]['param'] = file.list()
        bot.send_message(message.chat.id,
                         service_functions.audio_list_to_text(user_action[message.chat.id]['param']))
        bot.register_next_step_handler(message, edit_music)
    elif message.text:
        try:
            file_id = audio_files_list[int(message.text) - 1][0]
            file.delete(file_id)
            os.remove('./music/' + audio_files_list[int(message.text) - 1][1])
            bot.send_message(message.chat.id, 'The file has deleted')
            user_action[message.chat.id]['param'] = file.list()
            bot.send_message(message.chat.id,
                             service_functions.audio_list_to_text(user_action[message.chat.id]['param']))
            bot.register_next_step_handler(message, edit_music)
        except ValueError:
            bot.send_message(message.chat.id, 'Type a NUMBER')
            bot.register_next_step_handler(message, edit_music)
        except IndexError:
            bot.send_message(message.chat.id, 'There is no music with such number')
            bot.register_next_step_handler(message, edit_music)

if __name__ == '__main__':
    if not bot_config.getboolean('DEFAULT', 'test_version'):
        notification_list = admin.notification_list()
        for user_id in notification_list:
            bot.send_message(user_id, 'Bot is run')
        log.info('Notifications has sent')
    bot.polling(none_stop=True)
