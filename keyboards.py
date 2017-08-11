import telebot


def main(user):
    markup = telebot.types.ReplyKeyboardMarkup()
    random_quote_btn = telebot.types.KeyboardButton('Random quote')
    help_btn = telebot.types.KeyboardButton('Help')
    music_btn = telebot.types.KeyboardButton('Music')
    get_id_btn = telebot.types.KeyboardButton('My ID')
    status_btn = telebot.types.KeyboardButton("Bot's state")
    setting_btn = telebot.types.KeyboardButton('Settings')
    markup.row(random_quote_btn)
    markup.row(music_btn)
    markup.row(get_id_btn)
    markup.row(help_btn)
    if user == 'admin':
        markup.row(setting_btn)
    return markup


def setting(notifications_on):
    markup = telebot.types.ReplyKeyboardMarkup()
    add_quote_btn = telebot.types.KeyboardButton('Add a new quote')
    if notifications_on:
        notifications_btn = telebot.types.KeyboardButton('Disable notifications')
    else:
        notifications_btn = telebot.types.KeyboardButton('Enable notifications')
    back_btn = telebot.types.KeyboardButton('Back')
    markup.row(add_quote_btn)
    markup.row(notifications_btn)
    markup.row(back_btn)
    return markup
