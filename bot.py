from telegram.ext import Updater, CommandHandler, Dispatcher
from telegram import Bot, Update
import os


def start(bot: Bot, update: Update):
    bot.send_message(chat_id=update.message.chat_id, text='Hello! Tell me smth, please.')


def echo(bot: Bot, update: Update):
    bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id, text=update.message.text[6:])


if __name__ == '__main__':
    token = os.getenv('TELEGRAM_BOT_API_TOKEN', None)
    if not token:
        raise EnvironmentError('Need to export your telegram bot token as TELEGRAM_BOT_API_TOKEN enviroment variable.')
    updater = Updater(token=token)
    dispatcher = updater.dispatcher
    start_handler = CommandHandler('start', start)
    echo_handler = CommandHandler('echo', echo)
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(echo_handler)
    updater.start_polling()