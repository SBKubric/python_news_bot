import argparse
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import Bot, Update, ReplyKeyboardMarkup
import os
from news_collector import start_news_collector
from telegram.error import (TelegramError, Unauthorized, BadRequest,
                            TimedOut, ChatMigrated, NetworkError)
import logging

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

collector = start_news_collector()


def parse_args():
    parser = argparse.ArgumentParser(
        description="PyNewsBot v.0.0.1\nThis bot's job is to "
                    "provide you with fresh news about Python"
                    "and he loves it!")
    parser.add_argument('-v', '--verbose', action="store_true", help='Verbose mode')
    parser.add_argument('-s', '--silent', action="store_true", help='Silent mode')
    return parser.parse_args()


def get_random_fresh_post():
    return collector.get_random_fresh_post()


def start(bot: Bot, update: Update):
    keyboard = [
        ['/get_news'],
    ]
    bot.send_message(chat_id=update.message.chat_id,
                     text='I am the PyNewsBot and I am here'
                          'to provide fresh news about Python.',
                     reply_markup=ReplyKeyboardMarkup(keyboard=keyboard))


def unknown(bot: Bot, update: Update):
    bot.send_message(chat_id=update.message.chat_id,
                     text="Sorry, but I can't help you with that -_-")


def echo(bot: Bot, update: Update):
    bot.send_message(chat_id=update.message.chat_id,
                     reply_to_message_id=update.message.message_id,
                     text=update.message.text)


def get_news(bot: Bot, update: Update):
    post = get_random_fresh_post()
    message = '{}{}\n{}'.format(post.description[:250].replace('<br>', '\n'), '...',
                                post.url)
    bot.send_message(chat_id=update.message.chat_id, text=message)


def error_callback(bot, update, error):
    logger = logging.getLogger()
    try:
        raise error
    except Unauthorized as e:
        logger.error('Chat_id:{}\nUser message:{}\nError message:\n{}\n'.format(
            update.message.chat_id,
            update.message.text,
            e.message)
        )
    except BadRequest as e:
        logger.error('Chat_id:{}\nUser message:{}\nError message:\n{}\n'.format(
            update.message.chat_id,
            update.message.text,
            e.message)
        )
    except TimedOut as e:
        logger.error('Chat_id:{}\nUser message:{}\nError message:\n{}\n'.format(
            update.message.chat_id,
            update.message.text,
            e.message)
        )
    except NetworkError as e:
        logger.error('Chat_id:{}\nUser message:{}\nError message:\n{}\n'.format(
            update.message.chat_id,
            update.message.text,
            e.message)
        )
    except ChatMigrated as e:
        logger.error('Chat_id:{}\nUser message:{}\nError message:\n{}\n'.format(
            update.message.chat_id,
            update.message.text,
            e.message)
        )
    except TelegramError as e:
        logger.error('Chat_id:{}\nUser message:{}\nError message:\n{}\n'.format(
            update.message.chat_id,
            update.message.text,
            e.message)
        )


if __name__ == '__main__':
    args = parse_args()
    logger = logging.getLogger()
    if args.silent:
        logger.setLevel(logging.FATAL)
    else:
        if args.verbose:
            logger.setLevel(logging.DEBUG)
    token = os.environ.get('TELEGRAM_BOT_API_TOKEN', None)
    if not token:
        raise EnvironmentError(
            'Need to export your telegram bot token as TELEGRAM_BOT_API_TOKEN enviroment variable.')
    updater = Updater(token=token)
    dispatcher = updater.dispatcher
    start_handler = CommandHandler('start', start)
    get_news_handler = CommandHandler('get_news', get_news)
    echo_handler = MessageHandler(Filters.text, echo)
    unknown_handler = MessageHandler(Filters.command, unknown)
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(echo_handler)
    dispatcher.add_handler(get_news_handler)
    dispatcher.add_error_handler(error_callback)
    dispatcher.add_handler(unknown_handler)
    updater.start_polling(bootstrap_retries=5)
    logger.info('Started the bot')
