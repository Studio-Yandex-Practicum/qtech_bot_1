"""Главный модуль бота"""
import os

from db import session
from dotenv import load_dotenv
from handlers import (analytics, analytics_date, analytics_type,
                      back_to_previous_handler,
                      button_text_picture_doc_handler,
                      department_button_handler, info_buttons_handler,
                      message_handler, moscow_office_handler, start_handler)
from telegram.ext import (CallbackQueryHandler, CommandHandler, Filters,
                          MessageHandler, Updater)

load_dotenv()


def setup_handlers(dispatcher):
    """Установка всех обработчиков"""
    dispatcher.add_handler(CommandHandler('start', start_handler))
    dispatcher.add_handler(
        CallbackQueryHandler(moscow_office_handler, pattern='^(new_employee|old_employee)$')
    )
    dispatcher.add_handler(
        CallbackQueryHandler(info_buttons_handler, pattern='^(moscow_yes|moscow_no)$')
    )
    dispatcher.add_handler(
        CallbackQueryHandler(button_text_picture_doc_handler, pattern='^button_\\d+$')
    )
    dispatcher.add_handler(CallbackQueryHandler(
        department_button_handler, pattern='^department_button[a-z_]+$')
    )
    dispatcher.add_handler(CallbackQueryHandler(start_handler, pattern='to_start'))
    dispatcher.add_handler(CallbackQueryHandler(back_to_previous_handler, pattern='^to_previous$'))
    dispatcher.add_handler(
        CallbackQueryHandler(
            analytics,
            pattern='^(Total|Users|Messages|Events)$'
        )
    )
    dispatcher.add_handler(CallbackQueryHandler(analytics_date, pattern='^No_Date$'))
    dispatcher.add_handler(CallbackQueryHandler(analytics_type, pattern='^No_Type$'))
    dispatcher.add_handler(MessageHandler(Filters.all, message_handler))


def main():
    """Основная функция для запуска бота"""
    updater = Updater(os.getenv('BOT_TOKEN'), use_context=True)
    dispatcher = updater.dispatcher
    setup_handlers(dispatcher)
    updater.start_polling()
    updater.idle()
    session.close()


if __name__ == '__main__':
    main()
