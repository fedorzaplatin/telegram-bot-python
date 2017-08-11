import telebot


def setting(notifications_on):
    markup = telebot.types.ReplyKeyboardMarkup()

    add_quote_btn = telebot.types.KeyboardButton('Добавить цитату')
    edit_quotes_list_btn = telebot.types.KeyboardButton('Редактировать список цитат')
    edit_music = telebot.types.KeyboardButton('Редактировать команду music')
    if notifications_on:
        notifications_btn = telebot.types.KeyboardButton('Отключить оповещения о включении бота')
    else:
        notifications_btn = telebot.types.KeyboardButton('Включить оповещения о включении бота')
    back_btn = telebot.types.KeyboardButton('Назад')

    markup.row(add_quote_btn)
    markup.row(edit_quotes_list_btn)
    markup.row(edit_music)
    markup.row(notifications_btn)
    markup.row(back_btn)
    return markup
