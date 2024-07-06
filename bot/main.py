import os

from dotenv import load_dotenv
from telegram.ext import (
    Updater, CommandHandler, CallbackQueryHandler,
    MessageHandler, Filters)

from db import session
from handlers import (
    start_handler, moscow_office_handler, info_buttons_handler,
    back_to_previous_handler, button_text_handler,
    message_handler, department_button_handler)

load_dotenv()


def main():
    """Основная функция для запуска бота"""
    updater = Updater(os.getenv('BOT_TOKEN'), use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler('start', start_handler))
    dispatcher.add_handler(CallbackQueryHandler(
        moscow_office_handler,
        pattern='^(new_employee|old_employee)$'))
    dispatcher.add_handler(
        CallbackQueryHandler(info_buttons_handler,
                             pattern='^(moscow_yes|moscow_no)$'))
    dispatcher.add_handler(
        CallbackQueryHandler(button_text_handler, pattern='^button_\\d+$'))
    dispatcher.add_handler(MessageHandler(Filters.all, message_handler))
    dispatcher.add_handler(CallbackQueryHandler(
        department_button_handler,
        pattern='^department_button_(moscow_yes|moscow_no)$'))
    dispatcher.add_handler(CallbackQueryHandler(start_handler,
                                                pattern='to_start'))
    dispatcher.add_handler(CallbackQueryHandler(back_to_previous_handler,
                                                pattern='^to_previous$'))

    updater.start_polling()
    updater.idle()
    session.close()


if __name__ == '__main__':
    main()
