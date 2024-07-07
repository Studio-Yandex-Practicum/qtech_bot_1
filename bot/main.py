import os

from dotenv import load_dotenv
from telegram.ext import (
    Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters)

from db import session
from handlers import (
    handle_start, handle_moscow_office, handle_info_buttons,
    handle_back_to_previous, handle_button_text, handle_message,
    handle_department_buttons)

load_dotenv()


def setup_handlers(dispatcher):
    """Установка всех обработчиков"""
    dispatcher.add_handler(CommandHandler('start', handle_start))
    dispatcher.add_handler(CallbackQueryHandler(handle_moscow_office, pattern='^(new_employee|old_employee)$'))
    dispatcher.add_handler(CallbackQueryHandler(handle_info_buttons, pattern='^(moscow_yes|moscow_no)$'))
    dispatcher.add_handler(CallbackQueryHandler(handle_button_text, pattern='^button_\\d+$'))
    dispatcher.add_handler(CallbackQueryHandler(handle_department_buttons, pattern='^department_button$'))
    dispatcher.add_handler(CallbackQueryHandler(handle_start, pattern='to_start'))
    dispatcher.add_handler(CallbackQueryHandler(handle_back_to_previous, pattern='^to_previous$'))
    dispatcher.add_handler(MessageHandler(Filters.all, handle_message))


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
