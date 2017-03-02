from telegram.ext import Updater, CommandHandler, Dispatcher
from telegram import Bot, Update, ReplyKeyboardMarkup
import os
from news_collector import start_news_collector, NewsCollector

collector = start_news_collector()


def get_random_fresh_post():
    return collector.get_random_fresh_post()


def start(bot: Bot, update: Update):
    keyboard = [
        ['/get_news'],
    ]
    bot.send_message(chat_id=update.message.chat_id, text='I am the PyNewsBot and I am here'
                                                          'to provide fresh news about Python.',
                     reply_markup=ReplyKeyboardMarkup(keyboard=keyboard))


def echo(bot: Bot, update: Update):
    bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id, text=update.message.text[6:])


def get_news(bot: Bot, update: Update):
    post = get_random_fresh_post()
    bot.send_message(chat_id=update.message.chat_id, text=post.get('text', 'Bad post'))


if __name__ == '__main__':
    token = os.getenv('TELEGRAM_BOT_API_TOKEN', None)
    if not token:
        raise EnvironmentError('Need to export your telegram bot token as TELEGRAM_BOT_API_TOKEN enviroment variable.')
    updater = Updater(token=token)
    dispatcher = updater.dispatcher
    start_handler = CommandHandler('start', start)
    get_news_handler = CommandHandler('get_news', get_news)
    echo_handler = CommandHandler('echo', echo)
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(echo_handler)
    dispatcher.add_handler(get_news_handler)
    updater.start_polling()
